"""
test_minimization.py — Test suite terminal untuk DFA Minimizer.

Menjalankan 4 skenario uji:
  1. DFA yang dapat diminimasi (ada state ekuivalen)
  2. DFA yang sudah minimal (tidak ada yang bisa digabung)
  3. DFA dengan unreachable state
  4. DFA tidak valid (transisi tidak lengkap)

Jalankan dengan:
    python test_minimization.py
"""


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automata.minimizer import DFAMinimizer

# ─────────────────────────────────────────────────────────────────────────────
# Helper: Pretty Printer
# ─────────────────────────────────────────────────────────────────────────────

SEP  = '=' * 60
SEP2 = '-' * 60


def print_header(title: str) -> None:
    print(f'\n{SEP}')
    print(f'  {title}')
    print(f'{SEP}')


def print_dfa(dfa: dict, label: str) -> None:
    """Cetak komponen DFA ke terminal secara rapi."""
    print(f'\n  ┌─ {label}')
    print(f'  │  States      : {dfa["states"]}')
    print(f'  │  Alphabet    : {dfa["alphabet"]}')
    print(f'  │  Start       : {dfa["start_state"]}')
    print(f'  │  Accept      : {dfa["accept_states"]}')
    print(f'  │  Transitions :')
    for state, trans in dfa['transitions'].items():
        marker = ' ★' if state in dfa['accept_states'] else ''
        for sym, tgt in trans.items():
            print(f'  │    δ({state}{marker}, {sym}) = {tgt}')
    print(f'  └{"─" * 45}')


def print_table(table: list[dict]) -> None:
    """Cetak tabel distinguishability."""
    print(f'\n  Tabel Distinguishability (Table-Filling / Myhill-Nerode):')
    print(f'  {"Pasangan":<18} {"Status":<30} {"Keterangan"}')
    print(f'  {SEP2}')
    for row in table:
        p, q   = row['pair']
        status = 'Distinguishable' if row['distinguishable'] else 'Indistinguishable'
        mark   = '✗ (berbeda)'    if row['distinguishable'] else '✓ (ekuivalen, gabung)'
        print(f'  ({p}, {q}){"":<12} {status:<30} {mark}')


def print_iterations(iterations: list[dict]) -> None:
    """Cetak log iterasi table-filling."""
    print(f'\n  Log Iterasi Table-Filling:')
    for it in iterations:
        n      = it['iteration']
        marked = it['newly_marked_pairs']
        if not marked:
            print(f'  Iterasi {n}: tidak ada pasangan baru yang ditandai → konvergen.')
        else:
            print(f'  Iterasi {n}: {len(marked)} pasangan baru ditandai distinguishable:')
            for m in marked:
                p, q   = m['pair']
                sym    = m['via_symbol']
                r, s   = m['leads_to']
                print(f'    ({p}, {q}) via \'{sym}\' → ({r}, {s}) yang sudah distinguishable')


def print_stats(stats: dict) -> None:
    """Cetak statistik minimasi."""
    print(f'\n  Statistik Minimasi:')
    print(f'  {"Jumlah state original":<35}: {stats["original_state_count"]}')
    if stats['removed_unreachable']:
        print(f'  {"State unreachable dihapus":<35}: {stats["removed_unreachable"]}')
        print(f'  {"Setelah hapus unreachable":<35}: {stats["after_remove_unreachable"]}')
    print(f'  {"Jumlah state minimal":<35}: {stats["minimal_state_count"]}')
    print(f'  {"State dikurangi":<35}: {stats["states_reduced_by"]}')
    minimal_str = 'Ya ✓' if stats['is_already_minimal'] else 'Tidak, ada state yang digabung'
    print(f'  {"DFA sudah minimal sebelumnya?":<35}: {minimal_str}')


def print_merged_groups(groups: dict) -> None:
    """Cetak informasi penggabungan state."""
    if not groups:
        print(f'\n  Tidak ada state yang digabung (semua state distinguishable).')
        return
    print(f'\n  State yang Digabung (Equivalence Classes):')
    for rep, members in groups.items():
        print(f'    {members}  →  representatif: \'{rep}\'')


def run_test(test_name: str, minimizer: DFAMinimizer) -> dict | None:
    """
    Jalankan satu skenario uji dan cetak hasil lengkap ke terminal.

    Returns:
        dict | None: Hasil minimize() jika berhasil, None jika gagal.
    """
    print_header(test_name)

    result = minimizer.minimize()

    if not result['success']:
        print(f'\n  [GAGAL] Validasi DFA tidak lolos:')
        for err in result['error']:
            print(f'    • {err}')
        return None

    # ── DFA Original ────────────────────────────────────────────────
    print_dfa(result['original_dfa'], 'DFA Original (setelah hapus unreachable)')

    # ── Statistik ───────────────────────────────────────────────────
    print_stats(result['stats'])

    # ── Tabel distinguishability ────────────────────────────────────
    print_table(result['distinguishable_table'])

    # ── Log iterasi ─────────────────────────────────────────────────
    print_iterations(result['iterations'])

    # ── Penggabungan state ──────────────────────────────────────────
    print_merged_groups(result['merged_groups'])

    # ── DFA Minimal ─────────────────────────────────────────────────
    print_dfa(result['minimal_dfa'], 'DFA Minimal (Hasil Minimasi)')

    # ── Pemetaan state ──────────────────────────────────────────────
    print(f'\n  Pemetaan State (original → representatif):')
    for orig, rep in result['state_mapping'].items():
        marker = ' (digabung)' if orig != rep else ''
        print(f'    {orig} → {rep}{marker}')

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Skenario Uji 1 — DFA yang Dapat Diminimasi
# ─────────────────────────────────────────────────────────────────────────────
# Bahasa: string biner yang berakhiran '1'
# q0 ≡ q1,  q3 ≡ q4  (masing-masing indistinguishable)
# Seharusnya menghasilkan 2 state: {q0,q1} dan {q2} → {q3,q4}
# DFA 5 state → minimal 2 state

test1 = DFAMinimizer(
    states        = ['q0', 'q1', 'q2', 'q3', 'q4'],
    alphabet      = ['0', '1'],
    transitions   = {
        'q0': {'0': 'q1', '1': 'q2'},
        'q1': {'0': 'q1', '1': 'q2'},   # q0 ≡ q1
        'q2': {'0': 'q3', '1': 'q2'},
        'q3': {'0': 'q4', '1': 'q2'},
        'q4': {'0': 'q4', '1': 'q2'},   # q3 ≡ q4
    },
    start_state   = 'q0',
    accept_states = ['q2'],
)

result1 = run_test('TEST 1 — DFA Dapat Diminimasi (5 state → 2 state)', test1)


# ─────────────────────────────────────────────────────────────────────────────
# Skenario Uji 2 — DFA Sudah Minimal
# ─────────────────────────────────────────────────────────────────────────────
# Bahasa: string atas {a, b} yang mengandung substring 'ab'
# Semua state distinguishable → tidak ada yang bisa digabung

test2 = DFAMinimizer(
    states        = ['q0', 'q1', 'q2'],
    alphabet      = ['a', 'b'],
    transitions   = {
        'q0': {'a': 'q1', 'b': 'q0'},
        'q1': {'a': 'q1', 'b': 'q2'},
        'q2': {'a': 'q2', 'b': 'q2'},
    },
    start_state   = 'q0',
    accept_states = ['q2'],
)

run_test('TEST 2 — DFA Sudah Minimal (tidak ada penggabungan)', test2)


# ─────────────────────────────────────────────────────────────────────────────
# Skenario Uji 3 — DFA dengan Unreachable State
# ─────────────────────────────────────────────────────────────────────────────
# q3 adalah dead state yang tidak pernah terjangkau dari q0
# Pipeline harus menghapus q3 sebelum minimasi

test3 = DFAMinimizer(
    states        = ['q0', 'q1', 'q2', 'q3'],
    alphabet      = ['0', '1'],
    transitions   = {
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q2'},
        'q2': {'0': 'q2', '1': 'q2'},
        'q3': {'0': 'q3', '1': 'q3'},   # q3: tidak pernah dicapai dari q0
    },
    start_state   = 'q0',
    accept_states = ['q2'],
)

run_test('TEST 3 — DFA dengan Unreachable State (q3 tidak terjangkau)', test3)


# ─────────────────────────────────────────────────────────────────────────────
# Skenario Uji 4 — DFA Tidak Valid
# ─────────────────────────────────────────────────────────────────────────────
# Transisi tidak lengkap: q1 tidak punya transisi untuk simbol '1'

test4 = DFAMinimizer(
    states        = ['q0', 'q1', 'q2'],
    alphabet      = ['0', '1'],
    transitions   = {
        'q0': {'0': 'q1', '1': 'q2'},
        'q1': {'0': 'q0'},              # tidak ada transisi q1 --1-->
        'q2': {'0': 'q2', '1': 'q2'},
    },
    start_state   = 'q0',
    accept_states = ['q2'],
)

run_test('TEST 4 — DFA Tidak Valid (transisi tidak lengkap)', test4)


# ─────────────────────────────────────────────────────────────────────────────
# Ringkasan akhir
# ─────────────────────────────────────────────────────────────────────────────

print(f'\n{SEP}')
print(f'  RINGKASAN HASIL TEST')
print(f'{SEP}')

if result1:
    stats = result1['stats']
    mdfa  = result1['minimal_dfa']
    print(f'  Test 1 : {stats["original_state_count"]} state '
          f'→ {stats["minimal_state_count"]} state minimal')
    print(f'           States  : {mdfa["states"]}')
    print(f'           Start   : {mdfa["start_state"]}')
    print(f'           Accept  : {mdfa["accept_states"]}')

print(f'\n  Format to_dict() (kompatibel dengan kelas DFA):')
test1_fresh = DFAMinimizer(
    states        = ['q0', 'q1', 'q2', 'q3', 'q4'],
    alphabet      = ['0', '1'],
    transitions   = {
        'q0': {'0': 'q1', '1': 'q2'},
        'q1': {'0': 'q1', '1': 'q2'},
        'q2': {'0': 'q3', '1': 'q2'},
        'q3': {'0': 'q4', '1': 'q2'},
        'q4': {'0': 'q4', '1': 'q2'},
    },
    start_state   = 'q0',
    accept_states = ['q2'],
)
test1_fresh.minimize()
dfa_dict = test1_fresh.to_dict()
print(f'  {dfa_dict}')

print(f'\n  Format get_graph_data() (Cytoscape.js):')
graph = test1_fresh.get_graph_data()
nodes = [n for n in graph if 'source' not in n['data']]
edges = [e for e in graph if 'source' in e['data']]
print(f'  Nodes ({len(nodes)}): {[n["data"]["id"] for n in nodes]}')
print(f'  Edges ({len(edges)}): {[(e["data"]["source"], e["data"]["label"], e["data"]["target"]) for e in edges]}')

print(f'\n{SEP}\n')