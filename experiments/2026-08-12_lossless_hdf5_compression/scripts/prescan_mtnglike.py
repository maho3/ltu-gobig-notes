#!/usr/bin/env python
"""Read-only pre-scan of a suite before in-place compression. Classifies every
file: UNOPENABLE / EMPTY (0 datasets) / ALREADY (already filtered) / GOOD.
Writes the GOOD list (what the compressor should process) and a JSON report of
everything excluded, so the run never trips over a known-bad file mid-flight.
Header/metadata reads only — does not read dataset contents.
"""
import os, sys, json, glob
from multiprocessing import Pool
import h5py

SUITE_ROOT = os.environ.get("SUITE_ROOT",
    "/ocean/projects/phy240015p/mho1/cmass-ili/mtnglike/fastpm")
GLOB = os.environ.get("GLOB","nbody.h5")
OUT  = os.environ.get("OUTBASE",
    "/ocean/projects/phy240015p/mho1/compression_scratch/mtnglike_prescan")
NPROC= int(os.environ.get("NPROC","32"))

def classify(path):
    try:
        with h5py.File(path,"r") as f:
            ds=[]; f.visititems(lambda n,o: ds.append(n) if isinstance(o,h5py.Dataset) else None)
            if not ds:
                return (path,"EMPTY",0,None)
            # already compressed? (any dataset carries shuffle+gzip)
            comp = all((f[n].compression is not None) for n in ds)
            some = any((f[n].compression is not None) for n in ds)
            kind = "ALREADY" if comp else ("PARTIAL" if some else "GOOD")
            return (path,kind,len(ds),str(f[ds[0]].dtype))
    except Exception as e:
        return (path,"UNOPENABLE",0,f"{type(e).__name__}: {str(e)[:100]}")

def main():
    files=sorted(glob.glob(os.path.join(SUITE_ROOT,"**",GLOB),recursive=True))
    print(f"scanning {len(files)} files under {SUITE_ROOT}",flush=True)
    res=[]
    with Pool(NPROC) as pool:
        for r in pool.imap_unordered(classify,files,chunksize=8):
            res.append(r)
    by={}
    for _,k,_,_ in res: by[k]=by.get(k,0)+1
    good=sorted(p for p,k,_,_ in res if k=="GOOD")
    excluded=[dict(path=p,kind=k,ndsets=nd,info=info) for p,k,nd,info in res if k!="GOOD"]
    with open(OUT+"_good.txt","w") as f: f.write("\n".join(good)+("\n" if good else ""))
    with open(OUT+"_report.json","w") as f:
        json.dump(dict(suite=SUITE_ROOT,total=len(files),counts=by,
                       good=len(good),excluded=excluded),f,indent=2)
    print("counts:",by,flush=True)
    print(f"GOOD={len(good)} written to {OUT}_good.txt",flush=True)
    if excluded:
        print(f"EXCLUDED {len(excluded)} (see {OUT}_report.json):",flush=True)
        for e in excluded[:30]: print(f"  {e['kind']:11s} {e['path']}  {e['info'] or ''}",flush=True)
    print("PRESCAN_DONE",flush=True)

if __name__=="__main__": main()
