"""
Shared styling for ltu-gobig talk figures (PNG, slide-legible).

Adapted from /u/maho3/git/for_talk/scripts/talk_style.py, extended with the
label/parameter conventions used across ltu-gobig-notes.

Usage:
    from talk_style import apply_style, save, COLORS, PARAM
    apply_style()
    ...
    save(fig, 'my_figure')
"""

import os
import sys
import matplotlib as mpl

# Reuse the notes repo's k-cut / summary label helpers.
sys.path.insert(0, '/u/maho3/git/ltu-gobig-notes/scripts')

FIGDIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'figures')

# Two-panel figure size, chosen so two of these sit side by side on a 16:9
# slide (13.33in wide) with margins between them. Taller than wide overall.
FIGSIZE = (7.0, 5.6)

# For a figure that gets a slide to itself and can use the full content width.
FIGSIZE_WIDE = (11.0, 5.2)

# ── palette ───────────────────────────────────────────────────────────────────
COLORS = {
    'primary':  '#1b6ca8',   # blue
    'accent':   '#c44e52',   # red
    'green':    '#2a9d8f',
    'orange':   '#e76f51',
    'purple':   '#7d5ba6',
    'ideal':    '#444444',   # diagonal / reference lines
    'neutral':  '#555555',
    'band':     '#9ab8d6',
}

# Abacus cosmology classes keep the colors/markers used in the notes.
COSM = {
    'simple':   ('#1b6ca8', 'o', r'$\Lambda$CDM, $M_\nu=0$'),
    'mnu':      ('#e76f51', '^', r'$\Lambda$CDM, $M_\nu>0$'),
    'non_lcdm': ('#2a9d8f', 's', r'non-$\Lambda$CDM'),
}

CYCLE = ['#1b6ca8', '#2a9d8f', '#e76f51', '#c44e52', '#7d5ba6']

# ── parameters ────────────────────────────────────────────────────────────────
# theta column order: Omega_m, Omega_b, h, n_s, sigma_8 [, HOD..., noise]
PARAM = {0: r'$\Omega_m$', 1: r'$\Omega_b$', 2: r'$h$',
         3: r'$n_s$', 4: r'$\sigma_8$'}
PARAM_SHORT = {0: 'Om', 4: 's8'}
PRIMARY_PARAMS = [0, 4]


def apply_style():
    """Apply shared rcParams. Call once at the top of each figure script."""
    mpl.rcParams.update({
        'figure.dpi': 120,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',

        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans'],
        'font.size': 14,
        'axes.titlesize': 17,
        'axes.labelsize': 15,
        'xtick.labelsize': 13,
        'ytick.labelsize': 13,
        'legend.fontsize': 13,
        'figure.titlesize': 19,
        'mathtext.fontset': 'dejavusans',

        'lines.linewidth': 2.2,
        'lines.markersize': 7,
        'axes.linewidth': 1.2,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.prop_cycle': mpl.cycler(color=CYCLE),

        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 5,
        'ytick.major.size': 5,

        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.8,

        'legend.frameon': False,
    })


def save(fig, name, figdir=None, dpi=None):
    """Save as PNG (300 dpi unless `dpi` overrides) and print the path."""
    figdir = figdir or FIGDIR
    os.makedirs(figdir, exist_ok=True)
    path = os.path.join(figdir, name if name.endswith('.png') else name + '.png')
    fig.savefig(path, **({'dpi': dpi} if dpi else {}))
    print(f'saved {path}')
    return path
