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

def check_equivalence(dfa1, dfa2):
    """
    Cek apakah dua DFA ekuivalen.
    Metode: minimisasi keduanya lalu bandingkan strukturnya.
    Return: (is_equivalent: bool, reason: str)
    """
    # Pastikan alphabet sama
    if set(dfa1.alphabet) != set(dfa2.alphabet):
        return False, f'Alphabet berbeda: {sorted(dfa1.alphabet)} vs {sorted(dfa2.alphabet)}'

    # Gunakan product construction untuk cek ekuivalensi
    # Dua DFA ekuivalen jika tidak ada string yang diterima satu tapi ditolak lainnya
    # Cek dengan BFS pada product automaton
    queue = [(dfa1.start_state, dfa2.start_state)]
    visited = set()
    visited.add((dfa1.start_state, dfa2.start_state))

    while queue:
        s1, s2 = queue.pop(0)
        in_accept1 = s1 in dfa1.accept_states
        in_accept2 = s2 in dfa2.accept_states

        if in_accept1 != in_accept2:
            # Temukan string yang membedakan
            witness = _find_witness(dfa1, dfa2, s1, s2)
            return False, f'Ditemukan string yang membedakan: "{witness}"'

        for symbol in dfa1.alphabet:
            n1 = dfa1.transitions.get(s1, {}).get(symbol, 'dead')
            n2 = dfa2.transitions.get(s2, {}).get(symbol, 'dead')
            pair = (n1, n2)
            if pair not in visited:
                visited.add(pair)
                queue.append(pair)

    return True, 'Kedua DFA menerima bahasa yang persis sama'

def _find_witness(dfa1, dfa2, s1, s2):
    """Cari string contoh yang membedakan dua DFA (BFS)"""
    queue = [(s1, s2, '')]
    visited = {(s1, s2)}
    while queue:
        curr1, curr2, path = queue.pop(0)
        in1 = curr1 in dfa1.accept_states
        in2 = curr2 in dfa2.accept_states
        if in1 != in2:
            return path if path else 'ε'
        for sym in dfa1.alphabet:
            n1 = dfa1.transitions.get(curr1, {}).get(sym, 'dead')
            n2 = dfa2.transitions.get(curr2, {}).get(sym, 'dead')
            if (n1, n2) not in visited:
                visited.add((n1, n2))
                queue.append((n1, n2, path + sym))
    return '(tidak ditemukan)'