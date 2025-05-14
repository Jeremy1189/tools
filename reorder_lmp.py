# reorder_lmp.py
# -----------------------------------------------------------------------------
# Re‑order element types in a LAMMPS data (*.lmp) file **and** synchronise the
# "Atom Type Labels" / "Masses" / *Coeffs sections.
# -----------------------------------------------------------------------------
# 2025‑05‑14  PyCharm‑friendly edition v3.1 (Atom Type Labels now rewritten)
# -----------------------------------------------------------------------------
# Quick use:
#   1. Edit CFG below → ▶ Run in PyCharm (no CLI needed).
#   2. Or pass CLI args – they override CFG.
#   3. Or launch with nothing and the script will prompt.
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# -----------------------------------------------------------------------------
# Quick‑config block – leave empty strings to ignore
# -----------------------------------------------------------------------------
CFG = {
    "input":  "origin_frame_data/config.lmp",                     # e.g. "config.lmp"
    "output": "config_order.lmp",                     # e.g. "config_order.lmp"
    "order":  "Co Ni Al Ti Ta Nb Pb Bi",                     # e.g. "Co Ni Al Ti Ta Nb Pb Bi"
    "type_col": 1,                    # -1 = auto‑detect, 0‑based index otherwise
    "remap_coeffs": False,             # True / False
}

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def find_section(lines: List[str], regex: str) -> Optional[int]:
    patt = re.compile(regex, re.IGNORECASE)
    for idx, line in enumerate(lines):
        if patt.match(line):
            return idx
    return None


def parse_atom_type_labels(lines: List[str], start: int) -> Dict[int, str]:
    if start is None:
        return {}
    i = start + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    symbols: Dict[int, str] = {}
    while i < len(lines) and lines[i].strip():
        tid, sym, *_ = lines[i].split()
        symbols[int(tid)] = sym
        i += 1
    return symbols


def rewrite_atom_type_labels(lines: List[str], start: int, new_order: List[str]):
    """Rewrite the Atom Type Labels section to reflect new type IDs."""
    if start is None:
        return
    new_block = ["Atom Type Labels\n", "\n"]
    for new_id, sym in enumerate(new_order, 1):
        new_block.append(f"{new_id} {sym}\n")
    new_block.append("\n")
    end = start + 1
    while end < len(lines) and not lines[end].strip():
        end += 1
    while end < len(lines) and lines[end].strip():
        end += 1
    lines[start:end] = new_block


def parse_masses(lines: List[str], start: int):
    if start is None:
        return {}, {}
    i = start + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    masses: Dict[int, float] = {}
    symbols: Dict[int, str] = {}
    while i < len(lines) and lines[i].strip():
        body, *comment = lines[i].split('#', 1)
        tid, mass = body.split()[:2]
        masses[int(tid)] = float(mass)
        symbols[int(tid)] = comment[0].strip() if comment else ""
        i += 1
    return masses, symbols


def rewrite_masses(lines: List[str], start: int, masses_old: Dict[int, float],
                   symbols_old: Dict[int, str], new_order: List[str]):
    if start is None:
        return
    sym2old = {s: t for t, s in symbols_old.items()}
    block = ["Masses\n", "\n"]
    for new_id, sym in enumerate(new_order, 1):
        old_id = sym2old.get(sym)
        mass = masses_old.get(old_id, 0.0)
        block.append(f"{new_id} {mass:.8f} # {sym}\n")
    block.append("\n")
    end = start + 1
    while end < len(lines) and not lines[end].strip():
        end += 1
    while end < len(lines) and lines[end].strip():
        end += 1
    lines[start:end] = block


def build_map(sym_old: Dict[int, str], new_order: List[str]) -> Dict[int, int]:
    if sym_old:
        if set(sym_old.values()) != set(new_order):
            raise ValueError("--order does not match the element set in file")
        s2o = {s: t for t, s in sym_old.items()}
        return {s2o[s]: new for new, s in enumerate(new_order, 1)}
    return {old: new for new, old in enumerate(range(1, len(new_order) + 1), 1)}


def remap_block(lines: List[str], start: int, type_col: int, mapping: Dict[int, int]):
    if start is None:
        return
    i = start + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and lines[i].strip():
        if lines[i].lstrip().startswith('#'):
            i += 1
            continue
        parts = lines[i].split()
        parts[type_col] = str(mapping[int(parts[type_col])])
        lines[i] = ' '.join(parts) + '\n'
        i += 1


def auto_type_col(lines: List[str], atoms_start: int, old_type_ids):
    i = atoms_start + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    sample = lines[i].split()
    for idx, tok in enumerate(sample[1:], 1):
        if tok.isdigit() and int(tok) in old_type_ids:
            return idx
    raise RuntimeError('Cannot auto‑detect type column; pass --type-col.')

# -----------------------------------------------------------------------------
# Argument parsing (CLI > CFG > prompt)
# -----------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description='Re‑order element types in a LAMMPS data file.')
    parser.add_argument('input', nargs='?')
    parser.add_argument('output', nargs='?')
    parser.add_argument('--order')
    parser.add_argument('--type-col', type=int, default=-1)
    parser.add_argument('--remap-coeffs', action='store_true')

    if len(sys.argv) > 1:
        return parser.parse_args()

    if CFG['input'] and CFG['output'] and CFG['order']:
        lst = [CFG['input'], CFG['output'], '--order', CFG['order']]
        if CFG['type_col'] >= 0:
            lst += ['--type-col', str(CFG['type_col'])]
        if CFG['remap_coeffs']:
            lst += ['--remap-coeffs']
        return parser.parse_args(lst)

    # Interactive fallback
    print('[reorder_lmp]  Interactive prompt (no CLI, CFG incomplete).')
    inp = input('Input  .lmp file path  : ').strip()
    out = input('Output .lmp file path  : ').strip()
    order = input('New element order      : ').strip()
    tcol = input('Type-column index [?]  : ').strip()
    remap = input('Remap *Coeffs? [y/N]   : ').strip().lower() in {'y', 'yes'}
    lst = [inp, out, '--order', order]
    if tcol:
        lst += ['--type-col', tcol]
    if remap:
        lst += ['--remap-coeffs']
    return parser.parse_args(lst)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    args = parse_args()
    if not (args.input and args.output and args.order):
        raise ValueError('input/output/order required')

    new_order = re.split(r'[\s,]+', args.order.strip())
    if len(set(new_order)) != len(new_order):
        raise ValueError('Duplicate symbols in --order')

    lines = Path(args.input).read_text().splitlines(keepends=True)

    lbl_start = find_section(lines, r'^\s*Atom\s+Type\s+Labels\b')
    sym_old = parse_atom_type_labels(lines, lbl_start)

    mass_start = find_section(lines, r'^\s*Masses\b')
    mass_old, sym_from_mass = parse_masses(lines, mass_start)
    if not sym_old:
        sym_old = {t: s for t, s in sym_from_mass.items() if s}

    mapping = build_map(sym_old, new_order)

    atoms_start = find_section(lines, r'^\s*Atoms\b')
    if atoms_start is None:
        raise RuntimeError('No "Atoms" section found')

    tcol = args.type_col if args.type_col >= 0 else auto_type_col(lines, atoms_start, mapping.keys())
    remap_block(lines, atoms_start, tcol, mapping)

    # Optional: remap *Coeffs
    if args.remap_coeffs:
        coeff_specs = [
            (r'^\s*Pair\s+Coeffs\b',      0),
            (r'^\s*PairIJ\s+Coeffs\b',    1),
            (r'^\s*Bond\s+Coeffs\b',      0),
            (r'^\s*Angle\s+Coeffs\b',     0),
            (r'^\s*Dihedral\s+Coeffs\b',  0),
            (r'^\s*Improper\s+Coeffs\b',  0),
        ]
        for pattern, col in coeff_specs:
            section = find_section(lines, pattern)
            remap_block(lines, section, col, mapping)

    # Rewrite Masses (keep original masses)
    rewrite_atom_type_labels(lines, lbl_start, new_order)
    rewrite_masses(lines, mass_start, mass_old, sym_old or sym_from_mass, new_order)

    # Write file
    Path(args.output).write_text(''.join(lines))
    print(f'[reorder_lmp]  ✓ wrote {args.output}')


if __name__ == '__main__':
    main()
