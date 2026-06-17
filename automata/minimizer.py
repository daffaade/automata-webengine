from automata.dfa import DFA

def minimize_dfa(dfa):
    """
    Minimisasi DFA menggunakan algoritma Table-Filling (Myhill-Nerode).
    Return: (minimized DFA, steps list untuk visualisasi)
    """
    steps = []

    # Langkah 1: Hapus unreachable states
    reachable = _get_reachable_states(dfa)
    if len(reachable) < len(dfa.states):
        removed = set(dfa.states) - reachable
        steps.append({
            'step': 1,
            'description': f'Hapus unreachable states: {sorted(removed)}',
            'states': sorted(reachable)
        })
    else:
        steps.append({
            'step': 1,
            'description': 'Semua state reachable, tidak ada yang dihapus',
            'states': sorted(reachable)
        })

    # Filter ke reachable states saja
    states = sorted(reachable)
    transitions = {
        s: {sym: t for sym, t in dfa.transitions.get(s, {}).items() if t in reachable}
        for s in states
    }
    accept_states = [s for s in dfa.accept_states if s in reachable]
    non_accept = [s for s in states if s not in accept_states]

    # Langkah 2: Buat partisi awal
    partitions = []
    if accept_states:
        partitions.append(frozenset(accept_states))
    if non_accept:
        partitions.append(frozenset(non_accept))

    steps.append({
        'step': 2,
        'description': 'Partisi awal: accepting vs non-accepting states',
        'partitions': [sorted(p) for p in partitions]
    })

    # Langkah 3: Iterasi refinement
    iteration = 0
    while True:
        iteration += 1
        new_partitions = []
        changed = False

        for group in partitions:
            splits = _split_partition(group, partitions, transitions, dfa.alphabet)
            if len(splits) > 1:
                changed = True
            new_partitions.extend(splits)

        partitions = new_partitions

        steps.append({
            'step': f'3.{iteration}',
            'description': f'Iterasi {iteration}: {"partisi berubah" if changed else "partisi stabil"}',
            'partitions': [sorted(p) for p in partitions]
        })

        if not changed:
            break

    # Langkah 4: Bangun DFA minimal
    # Setiap partisi menjadi satu state
    def find_partition(state):
        for i, part in enumerate(partitions):
            if state in part:
                return i
        return -1

    new_states = [f'P{i}' for i in range(len(partitions))]
    new_start = f'P{find_partition(dfa.start_state)}'
    new_accept = list(set(
        f'P{find_partition(s)}' for s in accept_states
    ))

    new_transitions = {}
    for i, part in enumerate(partitions):
        rep = next(iter(part))  # ambil satu wakil dari partisi
        state_name = f'P{i}'
        new_transitions[state_name] = {}
        for symbol in dfa.alphabet:
            target = transitions.get(rep, {}).get(symbol)
            if target:
                new_transitions[state_name][symbol] = f'P{find_partition(target)}'

    steps.append({
        'step': 4,
        'description': f'DFA minimal dibuat: {len(new_states)} state(s)',
        'partitions': [sorted(p) for p in partitions],
        'new_states': new_states
    })

    min_dfa = DFA(
        states=new_states,
        alphabet=dfa.alphabet,
        transitions=new_transitions,
        start_state=new_start,
        accept_states=new_accept
    )

    return min_dfa, steps

def _get_reachable_states(dfa):
    """BFS/DFS untuk temukan semua reachable states"""
    reachable = {dfa.start_state}
    queue = [dfa.start_state]
    while queue:
        state = queue.pop(0)
        for symbol in dfa.alphabet:
            next_state = dfa.transitions.get(state, {}).get(symbol)
            if next_state and next_state not in reachable:
                reachable.add(next_state)
                queue.append(next_state)
    return reachable

def _split_partition(group, all_partitions, transitions, alphabet):
    """Coba split sebuah group berdasarkan transisi"""
    if len(group) <= 1:
        return [group]

    def partition_of(state):
        for i, part in enumerate(all_partitions):
            if state in part:
                return i
        return -1

    # Signature setiap state: tuple dari (partition index of targets for each symbol)
    def signature(state):
        return tuple(
            partition_of(transitions.get(state, {}).get(sym))
            for sym in sorted(alphabet)
        )

    groups = {}
    for state in group:
        sig = signature(state)
        if sig not in groups:
            groups[sig] = []
        groups[sig].append(state)

    return [frozenset(g) for g in groups.values()]

# ── Backward Compatibility ───────────────────────────────────────────────────
# Fungsi check_equivalence telah dipindahkan ke modul automata.equivalence
# agar lebih modular. Import di bawah ini memastikan kode lama yang mengimport
# check_equivalence dari minimizer.py tetap berfungsi normal.
from automata.equivalence import check_equivalence  # noqa: F401