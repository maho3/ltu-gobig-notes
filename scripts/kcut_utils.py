"""
Shared helpers for the dynamic k-cut directory convention.

A model tree is laid out as::

    <wdir>/<nbody>/<sim>/models/<tracer>/<summary>/<kcut>/...

where <summary> is a '+'-joined list of summary statistics (e.g.
``zPk0+zPk2+zPk4+zBk0``) and <kcut> encodes the k-space cut applied to each
observable.

Two k-cut naming conventions coexist on disk:

- Legacy (scalar) — one kmax for the whole feature vector::

      kmin-0.0_kmax-0.4

- Dynamic (mapping) — a different kmax per observable family, with ``def``
  abbreviating the ``default`` key::

      kmin-0.0_kmax-zBk=0.2__zPk=0.4

The plotting scripts used to assume a fixed scalar-kmax grid. These helpers let
them instead discover whatever (summary, k-cut) combinations happen to be on
disk and order them by increasing granularity, so the figures work for any
combination of saved experiment. The encoding mirrors ``kcut_dirname`` /
``resolve_kmax`` in ``ltu-cmass/cmass/infer/tools.py``.
"""

import os
from os.path import join, isdir

# Bispectrum triangle-configuration tags, stripped when resolving a summary's
# k-cut family (e.g. zEqBk0 -> zBk).
_BK_TAGS = ('Eq', 'Sq', 'Ss', 'Is')


# ── k-cut parsing ──────────────────────────────────────────────────────────────

def parse_kcut(dirname):
    """Parse a k-cut directory name into ``(kmin, kmax)``.

    ``kmax`` is a float for legacy scalar cuts, or a ``{family: kmax}`` dict for
    dynamic per-observable cuts (``def`` expanded back to ``default``). Returns
    ``None`` if the name is not a k-cut directory.
    """
    if not dirname.startswith('kmin-') or '_kmax-' not in dirname:
        return None
    kmin_str, kmax_str = dirname[len('kmin-'):].split('_kmax-', 1)
    try:
        kmin = float(kmin_str)
    except ValueError:
        return None
    if '=' in kmax_str:
        kmax = {}
        for part in kmax_str.split('__'):
            if '=' not in part:
                return None
            key, val = part.split('=', 1)
            if key == 'def':
                key = 'default'
            try:
                kmax[key] = float(val)
            except ValueError:
                return None
    else:
        try:
            kmax = float(kmax_str)
        except ValueError:
            return None
    return kmin, kmax


def is_mapping(kmax):
    return isinstance(kmax, dict)


def kmax_list(kmax):
    """All per-observable kmax values as a list."""
    return list(kmax.values()) if is_mapping(kmax) else [kmax]


def granularity(kmin, kmax):
    """Sort key for increasing granularity (spectral information) of a k-cut.

    Ordered primarily by the power-spectrum kmax, then by the remaining
    per-observable cuts (e.g. the bispectrum kmax) in ascending order. So k-cuts
    sort by increasing Pk cut first, and within a fixed Pk cut by increasing Bk
    cut. A scalar cut applies the same kmax to every observable.
    """
    return (pk_kmax(kmax), tuple(sorted(kmax_list(kmax))))


def _kcut_keys(summ):
    """Candidate mapping keys for a summary, in decreasing specificity.

    e.g. ``zEqBk0`` -> ``['zEqBk', 'zBk', 'default']``.
    """
    keys = []
    family = summ.rstrip('0123456789')
    if family:
        keys.append(family)
        for tag in _BK_TAGS:
            if tag in family:
                keys.append(family.replace(tag, '', 1))
                break
    keys.append('default')
    return keys


def resolve_kmax(kmax, summ):
    """Resolve the kmax applied to a single summary within a k-cut.

    Scalar ``kmax`` applies to every summary; a mapping is keyed by observable
    family (``zPk``, ``zBk``, ...), stripped of triangle tags, or ``default``.
    Falls back to any available value if no key matches.
    """
    if not is_mapping(kmax):
        return kmax
    for key in _kcut_keys(summ):
        if key in kmax:
            return kmax[key]
    return next(iter(kmax.values()))


def pk_kmax(kmax):
    """kmax applied to the power-spectrum family (a common numeric axis, since
    every summary here contains zPk)."""
    return resolve_kmax(kmax, 'zPk0')


def kcut_label(kmin, kmax, multiline=True):
    """Short human-readable label for a k-cut, for plot titles/ticks."""
    if not is_mapping(kmax):
        return f'k<{kmax:g}'
    sep = '\n' if multiline else ', '
    return sep.join(f'{k}<{kmax[k]:g}' for k in sorted(kmax))


# ── discovery ──────────────────────────────────────────────────────────────────

def summary_sort_key(summary):
    """Order summaries by increasing feature complexity: fewer components first,
    power-spectrum-only before bispectrum, then alphabetically."""
    parts = summary.split('+')
    has_bk = any(('Bk' in p or 'Qk' in p) for p in parts)
    return (len(parts), int(has_bk), summary)


def discover_summaries(models_tracer_dir):
    """List summary subdirectories present, ordered by increasing complexity."""
    if not isdir(models_tracer_dir):
        return []
    summ = [d for d in os.listdir(models_tracer_dir)
            if isdir(join(models_tracer_dir, d))]
    return sorted(summ, key=summary_sort_key)


def discover_kcuts(summary_dir):
    """List ``(dirname, kmin, kmax)`` k-cuts present under a summary directory,
    ordered by increasing granularity."""
    if not isdir(summary_dir):
        return []
    out = []
    for d in os.listdir(summary_dir):
        parsed = parse_kcut(d)
        if parsed is None or not isdir(join(summary_dir, d)):
            continue
        out.append((d, parsed[0], parsed[1]))
    out.sort(key=lambda t: granularity(t[1], t[2]))
    return out


def select_kcut(summary_dir, ref_pk_kmax):
    """Pick the ``(dirname, kmin, kmax)`` whose power-spectrum kmax best matches
    ``ref_pk_kmax`` (ties broken toward lower granularity). Returns ``None`` if
    the summary directory has no k-cuts.

    Used to hold a reference kmax fixed while varying summary complexity, even
    though each summary encodes that cut under a different directory name.
    """
    kcuts = discover_kcuts(summary_dir)
    if not kcuts:
        return None
    return min(kcuts, key=lambda t: (abs(pk_kmax(t[2]) - ref_pk_kmax),
                                     granularity(t[1], t[2])))


# ── labels ─────────────────────────────────────────────────────────────────────

def simple(label):
    """Prettify a summary string for plot labels."""
    if isinstance(label, list):
        return [simple(l) for l in label]
    label = label.replace('nbar', r'$\bar{n}$')
    label = label.replace('zPk0+zPk2+zPk4', r'$zP_{0,2,4}$')
    label = label.replace('zPk0', r'$zP_{0}$')
    label = label.replace('zEqBk0', r'$zEqB_{0}$')
    label = label.replace('zSqBk0', r'$zSqB_{0}$')
    label = label.replace('zBk0', r'$zB_{0}$')
    label = label.replace('zQk0', r'$zQ_{0}$')
    label = label.replace('+', ', ')
    return label
