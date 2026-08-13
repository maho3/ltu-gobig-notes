#!/usr/bin/env python
"""In-place lossless compressor: for each .h5 file under SUITE_ROOT, compress to
a temp in the SAME directory, bit-verify against the original (arrays, dtypes,
attrs, filters), then ATOMICALLY replace the original. Peak extra space = one
temp per worker, so a whole suite is compressed without ever holding a full 2nd
copy (needed: only ~3.8 TB overhead on Ocean).

Safety (single-copy-safe by construction): the original is never removed until a
bit-identical, filter-verified temp exists; on ANY verification failure the temp
is deleted, the original is left untouched, and the run ABORTS immediately
(ground rule 4). Resumable: files already carrying SHUFFLE+DEFLATE are skipped.

Env: SUITE_ROOT (required), NPROC (default 16), GLOB (default '*.h5').
"""
import os, sys, json, time, hashlib, subprocess, glob, signal
from multiprocessing import Pool
import numpy as np, h5py

SUITE_ROOT = os.environ["SUITE_ROOT"].rstrip("/")
NPROC      = int(os.environ.get("NPROC","16"))
GLOB       = os.environ.get("GLOB","*.h5")
LOG        = os.environ.get("LOG", os.path.join(
    "/ocean/projects/phy240015p/mho1/compression_scratch",
    "inplace_"+SUITE_ROOT.strip("/").replace("/","__")+".jsonl"))
TMPSUF     = ".tmp_compress"

def chunk_for(shape):
    if len(shape)>=3 and shape[0]==shape[1]==shape[2]:
        c=max(1,shape[0]//4); return "x".join(map(str,[c,c,c]+list(shape[3:])))
    r=min(65536,shape[0]); return "x".join(map(str,[r]+list(shape[1:])))

def dsets(path):
    out=[]
    with h5py.File(path,"r") as f:
        f.visititems(lambda n,o: out.append(n) if isinstance(o,h5py.Dataset) else None)
    return out

def verify_filters(path):
    import re
    p=subprocess.run(["h5dump","-p","-H",path],capture_output=True,text=True).stdout
    res={}; stack=[]; cur=None; cd=None; depth=0
    for line in p.splitlines():
        s=line.strip()
        mg=re.match(r'GROUP "([^"]*)" \{',s); md=re.match(r'DATASET "([^"]*)" \{',s)
        if mg: stack.append((mg.group(1),depth))
        elif md:
            parts=[g for g,_ in stack if g!="/"]; cur="/".join(parts+[md.group(1)]); cd=depth
            res[cur]={"shuf":False,"defl":False}
        elif cur is not None:
            if "PREPROCESSING SHUFFLE" in s: res[cur]["shuf"]=True
            if "COMPRESSION DEFLATE" in s:   res[cur]["defl"]=True
        depth+=s.count("{")-s.count("}")
        while stack and depth<=stack[-1][1]: stack.pop()
        if cur is not None and depth<=cd: cur=None
    return res

def has_filters(path):
    p=subprocess.run(["h5dump","-p","-H",path],capture_output=True,text=True).stdout
    return ("PREPROCESSING SHUFFLE" in p) and ("COMPRESSION DEFLATE" in p)

def attrs_map(path):
    d={}
    with h5py.File(path,"r") as f:
        d["/"]={k:f.attrs[k] for k in f.attrs}
        f.visititems(lambda name,obj: d.__setitem__(name,{k:obj.attrs[k] for k in obj.attrs}))
    return d

def sha256(path, buf=1<<22):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(buf),b""): h.update(b)
    return h.hexdigest()


def process(orig):
    rel=os.path.relpath(orig,SUITE_ROOT)
    tmp=orig+TMPSUF
    r={"rel":rel}
    try:
        if has_filters(orig):
            r["status"]="ALREADY"; return r
        ods=dsets(orig)
        if not ods:                      # empty/failed file — never touch it
            r["status"]="EMPTY_SKIP"; return r
        DO_SHA=os.environ.get("VERIFY_SHA","1")=="1"
        r["orig_sha256"]=sha256(orig) if DO_SHA else None
        r["orig_bytes"]=os.path.getsize(orig)
        oattrs=attrs_map(orig)
        # build per-object filter args
        args=[]
        with h5py.File(orig,"r") as f:
            odtypes={n:f[n].dtype for n in ods}
            for n in ods:
                args+=["-f",f"{n}:SHUF","-f",f"{n}:GZIP=4","-l",f"{n}:CHUNK={chunk_for(f[n].shape)}"]
        if os.path.exists(tmp): os.remove(tmp)
        p=subprocess.run(["h5repack"]+args+[orig,tmp],capture_output=True,text=True)
        if p.returncode!=0: raise RuntimeError("h5repack: "+p.stderr[-200:])
        # verify filters on tmp
        vf=verify_filters(tmp)
        bad=[n for n in ods if not (vf.get(n,{}).get("shuf") and vf.get(n,{}).get("defl"))]
        if bad: raise RuntimeError(f"filters missing on {bad}")
        # bit-exact arrays + dtypes + shapes preserved (decompressed values compared)
        with h5py.File(orig,"r") as fa, h5py.File(tmp,"r") as fb:
            tds=set(); fb.visititems(lambda n,o: tds.add(n) if isinstance(o,h5py.Dataset) else None)
            if set(ods)!=tds: raise RuntimeError("dataset set changed")
            for n in ods:
                if fb[n].dtype!=odtypes[n]: raise RuntimeError(f"dtype changed {n}: {odtypes[n]}->{fb[n].dtype}")
                ao=fa[n][...]; bo=fb[n][...]
                if ao.shape!=bo.shape: raise RuntimeError(f"shape changed {n}: {ao.shape}->{bo.shape}")
                if not np.array_equal(ao,bo): raise RuntimeError(f"array mismatch {n}")
                ao=bo=None  # free before next dataset / h5diff (8GB files)
        # optional independent 2nd verifier: HDF5's own h5diff (C impl). Off by
        # default; set VERIFY_H5DIFF=1 for an independent cross-check on
        # high-value single-copy suites (doubles read I/O).
        if os.environ.get("VERIFY_H5DIFF","0")=="1":
            dp=subprocess.run(["h5diff","-q",orig,tmp],capture_output=True,text=True)
            if dp.returncode!=0:
                raise RuntimeError(f"h5diff rc={dp.returncode}: {dp.stdout[-160:]}{dp.stderr[-160:]}")
        # attrs preserved
        tattrs=attrs_map(tmp)
        if set(oattrs)!=set(tattrs): raise RuntimeError("attr node set changed")
        for node in oattrs:
            if set(oattrs[node])!=set(tattrs[node]): raise RuntimeError(f"attr keys changed at {node}")
            for k in oattrs[node]:
                if not np.array_equal(np.asarray(oattrs[node][k]),np.asarray(tattrs[node][k])):
                    raise RuntimeError(f"attr value changed at {node}:{k}")
        r["comp_bytes"]=os.path.getsize(tmp)
        r["comp_sha256"]=sha256(tmp) if DO_SHA else None
        r["ratio"]=round(r["orig_bytes"]/r["comp_bytes"],4)
        # ATOMIC in-place replace
        os.replace(tmp,orig)
        # post-replace integrity (sha optional; filter re-check always)
        if DO_SHA and sha256(orig)!=r["comp_sha256"]: raise RuntimeError("post-replace sha mismatch")
        if not has_filters(orig): raise RuntimeError("post-replace filters missing")
        r["status"]="COMPRESSED"
    except Exception as e:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except: pass
        r["status"]="FAIL"; r["error"]=str(e)
    return r

def main():
    # SHARD/NSHARD let a SLURM job array split one suite across many nodes;
    # each task takes a strided, disjoint subset (balances file sizes).
    NSHARD=int(os.environ.get("NSHARD","1")); SHARD=int(os.environ.get("SHARD","0"))
    FILELIST=os.environ.get("FILELIST","")   # explicit pre-scanned good-file list
    if FILELIST:
        allfiles=[l.strip() for l in open(FILELIST) if l.strip()]
    else:
        allfiles=sorted(glob.glob(os.path.join(SUITE_ROOT,"**",GLOB),recursive=True))
    allfiles=[f for f in allfiles if not f.endswith(TMPSUF)]
    files=allfiles[SHARD::NSHARD]            # this shard's disjoint subset
    # clean stray temps from a prior interrupted run -- ONLY for THIS shard's own
    # files. A global glob would race with concurrently-running shards and delete
    # their in-flight temps (this caused spurious aborts in job 42806533).
    for f in files:
        t=f+TMPSUF
        if os.path.exists(t): os.remove(t); print("removed stray tmp",t,flush=True)
    log=LOG if NSHARD==1 else LOG.replace(".jsonl",f".shard{SHARD}of{NSHARD}.jsonl")
    print(f"SUITE={SUITE_ROOT}\nshard {SHARD}/{NSHARD}: {len(files)} of {len(allfiles)} files, "
          f"FILELIST={'yes' if FILELIST else 'no'}, VERIFY_H5DIFF={os.environ.get('VERIFY_H5DIFF','0')}, "
          f"NPROC={NPROC}, host={os.uname().nodename}",flush=True)
    logf=open(log,"a")
    n=ncomp=nalr=nfail=0; osum=csum=0; t0=time.time(); aborted=False
    pool=Pool(NPROC)
    try:
        for r in pool.imap_unordered(process,files,chunksize=1):
            logf.write(json.dumps(r)+"\n"); logf.flush(); n+=1
            if r["status"]=="COMPRESSED":
                ncomp+=1; osum+=r["orig_bytes"]; csum+=r["comp_bytes"]
            elif r["status"] in ("ALREADY","EMPTY_SKIP"):
                nalr+=1
                if r["status"]=="EMPTY_SKIP": print(f"EMPTY_SKIP {r['rel']}",flush=True)
            else:
                nfail+=1
                print(f"FAIL {r['rel']}: {r.get('error')}",flush=True)
                print("ABORTING on first failure (ground rule 4). Original left untouched.",flush=True)
                pool.terminate(); aborted=True; break
            if n%200==0:
                print(f"[{time.strftime('%H:%M:%S')}] {n}/{len(files)} "
                      f"COMPRESSED={ncomp} ALREADY={nalr} {time.time()-t0:.0f}s "
                      f"ratio={osum/max(csum,1):.4f} freed={ (osum-csum)/1e9:.2f}GB",flush=True)
    finally:
        if not aborted: pool.close()
        pool.join()
    print(f"INPLACE DONE: COMPRESSED={ncomp} ALREADY={nalr} FAIL={nfail} of {len(files)}; "
          f"orig={osum/1e9:.2f}GB comp={csum/1e9:.2f}GB freed={(osum-csum)/1e9:.2f}GB "
          f"ratio={osum/max(csum,1):.4f}; {time.time()-t0:.0f}s"
          + ("  [ABORTED]" if aborted else ""),flush=True)
    print("ALLDONE_INPLACE" if not aborted else "ABORTED_INPLACE",flush=True)
    sys.exit(1 if aborted else 0)

if __name__=="__main__": main()
