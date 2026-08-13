#!/usr/bin/env python
"""
Relocate the misplaced Globus sync out of  L3000-N384/1335/<lhid>/  into its
intended home  L3000-N384/<lhid>/ .

Context: a Globus sync of another DB version was accidentally written one level
too deep, under the (legitimate) lhid directory `1335/`. Each nested subdir
`1335/<lhid>/` holds an `nbody.h5` (+ `config.yaml`). We move each nested lhid's
files up to `L3000-N384/<lhid>/`, OVERWRITING any existing file there (per
request -- even replacing an already-compressed nbody.h5 with this uncompressed
one; a backup exists). lhid 1335's OWN files (`1335/nbody.h5`, `1335/config.yaml`)
are left untouched.

SAFETY / REVIEW:
  * DRY-RUN by default: prints the full plan and writes it to a TSV log, but
    moves nothing. Pass --execute to actually perform the moves.
  * Moves are os.replace() = atomic rename on the same filesystem: instant, no
    data copied, no partial state. Overwrite is atomic.
  * After each nested lhid's files move, its now-empty `1335/<lhid>/` dir is
    removed. `1335/` itself is kept (still holds lhid 1335's own data).
  * Post-move check: destination exists with the right size and source is gone.
  * Idempotent: if a source was already moved, it's skipped.

Usage:
    python relocate_1335.py            # DRY-RUN: show plan, write log, move nothing
    python relocate_1335.py --execute  # actually move

Reverse (if ever needed): you have a backup; also relocate_1335_log.tsv records
every src->dst so moves could be scripted back.
"""
import os, sys

BASE      = "/ocean/projects/phy240015p/mho1/cmass-ili/mtnglike/fastpm/L3000-N384"
CONTAINER = os.path.join(BASE, "1335")          # the misplaced-sync container dir
LOG       = "/ocean/projects/phy240015p/mho1/compression_scratch/relocate_1335_log.tsv"
EXECUTE   = "--execute" in sys.argv

def main():
    if not os.path.isdir(CONTAINER):
        sys.exit(f"ERROR: {CONTAINER} not found")

    # Only the NESTED lhid subdirectories -- this naturally excludes 1335's own
    # files (1335/nbody.h5, 1335/config.yaml), which are plain files, not dirs.
    subdirs = sorted(d for d in os.listdir(CONTAINER)
                     if os.path.isdir(os.path.join(CONTAINER, d)))

    mode = "EXECUTE" if EXECUTE else "DRY-RUN"
    print(f"[{mode}] {len(subdirs)} nested lhid dirs under {CONTAINER}")
    if len(subdirs) == 0:
        sys.exit("nothing to do")

    log = open(LOG, "w")
    log.write("action\tlhid\tfile\tsrc\tdst\tbytes\toverlap\n")

    n_lhid = n_overlap = n_new = n_files = n_err = 0
    moved_bytes = 0
    shown = 0

    for lhid in subdirs:
        if lhid == "1335":
            # would map to 1335/ itself and could clobber the container's own
            # file -- refuse. (Not expected among the synced lhids.)
            print(f"  SKIP subdir named '1335' (would clobber container's own file)")
            continue

        src_dir = os.path.join(CONTAINER, lhid)
        dst_dir = os.path.join(BASE, lhid)
        dst_nbody_exists = os.path.exists(os.path.join(dst_dir, "nbody.h5"))

        files = sorted(f for f in os.listdir(src_dir)
                       if os.path.isfile(os.path.join(src_dir, f)))
        if not files:
            continue

        n_lhid += 1
        if dst_nbody_exists: n_overlap += 1
        else:               n_new += 1

        for fn in files:
            src = os.path.join(src_dir, fn)
            dst = os.path.join(dst_dir, fn)
            overlap = os.path.exists(dst)
            sz = os.path.getsize(src)
            act = "OVERWRITE" if overlap else "NEW"
            log.write(f"{act}\t{lhid}\t{fn}\t{src}\t{dst}\t{sz}\t{overlap}\n")
            # print a sample so a dry-run isn't 1000 lines
            if shown < 12 or lhid == subdirs[-1]:
                print(f"  {act:9s} {lhid}/{fn}  {sz/1024**3:6.2f} GB  ->  {dst}")
                shown += 1
            n_files += 1

            if EXECUTE:
                try:
                    os.makedirs(dst_dir, exist_ok=True)
                    os.replace(src, dst)            # atomic overwrite (same FS)
                    if not (os.path.exists(dst) and os.path.getsize(dst) == sz
                            and not os.path.exists(src)):
                        raise RuntimeError("post-move verification failed")
                    moved_bytes += sz
                except Exception as e:
                    n_err += 1
                    print(f"    ERROR moving {src}: {e}")
                    log.write(f"ERROR\t{lhid}\t{fn}\t{src}\t{dst}\t{sz}\t{overlap}\t{e}\n")

        # remove the emptied nested subdir
        if EXECUTE:
            try:
                if not os.listdir(src_dir):
                    os.rmdir(src_dir)
            except Exception as e:
                print(f"    (could not rmdir {src_dir}: {e})")

    log.close()
    verb = "MOVED" if EXECUTE else "WOULD MOVE"
    print(f"\n[{mode}] {verb}: {n_lhid} lhid dirs "
          f"({n_overlap} overwrite existing, {n_new} new), "
          f"{n_files} files, errors={n_err}")
    if EXECUTE:
        print(f"  relocated {moved_bytes/1024**4:.2f} TB (rename, instant).")
        print(f"  1335/ now holds only lhid-1335's own nbody.h5/config.yaml.")
    print(f"  full plan/audit log: {LOG}")
    if not EXECUTE:
        print("\n  This was a DRY-RUN -- nothing moved. Re-run with --execute to move.")

if __name__ == "__main__":
    main()
