from automata.dfa import DFA


def check_equivalence(dfa1, dfa2):
    """
    Memeriksa apakah dua DFA ekuivalen menggunakan Product Construction.

    Metode:
      Dua DFA dikatakan ekuivalen jika dan hanya jika keduanya menerima
      bahasa (language) yang persis sama. Algoritma ini membangun
      product automaton secara implisit dengan BFS pada pasangan state
      (s1, s2) dari kedua DFA. Jika ditemukan pasangan di mana satu
      state menerima dan yang lain menolak, maka kedua DFA TIDAK ekuivalen.

    Args:
        dfa1 (DFA): DFA pertama.
        dfa2 (DFA): DFA kedua.

    Returns:
        tuple: (is_equivalent: bool, reason: str)
    """
    # Pastikan alphabet sama
    if set(dfa1.alphabet) != set(dfa2.alphabet):
        return False, f'Alphabet berbeda: {sorted(dfa1.alphabet)} vs {sorted(dfa2.alphabet)}'

    # BFS pada product automaton
    queue = [(dfa1.start_state, dfa2.start_state)]
    visited = set()
    visited.add((dfa1.start_state, dfa2.start_state))

    while queue:
        s1, s2 = queue.pop(0)
        in_accept1 = s1 in dfa1.accept_states
        in_accept2 = s2 in dfa2.accept_states

        if in_accept1 != in_accept2:
            # Temukan witness string yang membedakan
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


def get_equivalence_details(dfa1, dfa2):
    """
    Versi detail dari check_equivalence() yang mengembalikan informasi
    lengkap tentang proses pemeriksaan ekuivalensi, termasuk langkah-langkah
    BFS pada product automaton.

    Informasi yang dikembalikan:
      - is_equivalent      : bool  — apakah kedua DFA ekuivalen
      - reason             : str   — penjelasan hasil
      - witness            : str   — string pembeda (jika tidak ekuivalen)
      - steps              : list  — langkah-langkah BFS product construction
      - visited_pairs      : list  — semua pasangan (s1, s2) yang dikunjungi
      - dfa1_info          : dict  — ringkasan DFA 1
      - dfa2_info          : dict  — ringkasan DFA 2

    Args:
        dfa1 (DFA): DFA pertama.
        dfa2 (DFA): DFA kedua.

    Returns:
        dict: Struktur lengkap hasil pemeriksaan ekuivalensi.
    """
    steps = []
    visited_pairs = []

    # ── Langkah 0: Validasi alphabet ────────────────────────────────────────
    if set(dfa1.alphabet) != set(dfa2.alphabet):
        steps.append({
            'step': 0,
            'description': 'Pemeriksaan alphabet',
            'detail': f'Alphabet DFA 1 = {sorted(dfa1.alphabet)}, '
                      f'Alphabet DFA 2 = {sorted(dfa2.alphabet)}',
            'result': 'GAGAL — alphabet tidak sama'
        })
        return {
            'is_equivalent': False,
            'reason': f'Alphabet berbeda: {sorted(dfa1.alphabet)} vs {sorted(dfa2.alphabet)}',
            'witness': None,
            'steps': steps,
            'visited_pairs': [],
            'dfa1_info': _dfa_summary(dfa1),
            'dfa2_info': _dfa_summary(dfa2)
        }

    steps.append({
        'step': 0,
        'description': 'Pemeriksaan alphabet',
        'detail': f'Alphabet sama: {sorted(dfa1.alphabet)}',
        'result': 'OK'
    })

    # ── Langkah 1+: BFS pada product automaton ──────────────────────────────
    queue = [(dfa1.start_state, dfa2.start_state, '')]
    visited = set()
    visited.add((dfa1.start_state, dfa2.start_state))
    parent = {}  # Untuk trace-back witness string
    step_num = 1
    found_witness = None

    while queue:
        s1, s2, path_str = queue.pop(0)
        in_accept1 = s1 in dfa1.accept_states
        in_accept2 = s2 in dfa2.accept_states

        pair_info = {
            'state_dfa1': s1,
            'state_dfa2': s2,
            'accept_dfa1': in_accept1,
            'accept_dfa2': in_accept2,
            'path': path_str
        }
        visited_pairs.append(pair_info)

        if in_accept1 != in_accept2:
            # Temukan witness — string yang membedakan perilaku
            found_witness = path_str if path_str else 'ε (string kosong)'

            steps.append({
                'step': step_num,
                'description': f'Periksa pasangan ({s1}, {s2})',
                'detail': f'DFA 1: {s1} {"∈" if in_accept1 else "∉"} F₁, '
                          f'DFA 2: {s2} {"∈" if in_accept2 else "∉"} F₂',
                'result': f'TIDAK EKUIVALEN — ditemukan perbedaan pada string "{found_witness}"'
            })

            return {
                'is_equivalent': False,
                'reason': f'Ditemukan string yang membedakan: "{found_witness}"',
                'witness': found_witness,
                'steps': steps,
                'visited_pairs': visited_pairs,
                'dfa1_info': _dfa_summary(dfa1),
                'dfa2_info': _dfa_summary(dfa2)
            }

        step_detail_parts = [
            f'DFA 1: {s1} {"∈" if in_accept1 else "∉"} F₁, '
            f'DFA 2: {s2} {"∈" if in_accept2 else "∉"} F₂ → sama'
        ]

        # Eksplorasi semua simbol
        transitions_explored = []
        for symbol in sorted(dfa1.alphabet):
            n1 = dfa1.transitions.get(s1, {}).get(symbol, 'dead')
            n2 = dfa2.transitions.get(s2, {}).get(symbol, 'dead')
            pair = (n1, n2)
            new_path = path_str + symbol

            transitions_explored.append(
                f'δ₁({s1},{symbol})={n1}, δ₂({s2},{symbol})={n2}'
            )

            if pair not in visited:
                visited.add(pair)
                queue.append((n1, n2, new_path))

        steps.append({
            'step': step_num,
            'description': f'Periksa pasangan ({s1}, {s2})',
            'detail': '; '.join(step_detail_parts),
            'transitions': transitions_explored,
            'result': 'OK — status penerimaan sama'
        })

        step_num += 1

    # Semua pasangan sudah diperiksa — ekuivalen
    steps.append({
        'step': step_num,
        'description': 'Kesimpulan',
        'detail': f'Semua {len(visited_pairs)} pasangan state telah diperiksa',
        'result': 'EKUIVALEN — tidak ditemukan perbedaan'
    })

    return {
        'is_equivalent': True,
        'reason': 'Kedua DFA menerima bahasa yang persis sama',
        'witness': None,
        'steps': steps,
        'visited_pairs': visited_pairs,
        'dfa1_info': _dfa_summary(dfa1),
        'dfa2_info': _dfa_summary(dfa2)
    }


def _find_witness(dfa1, dfa2, target_s1, target_s2):
    """
    Mencari string contoh (witness) yang membedakan dua DFA.
    BFS dari start state kedua DFA hingga mencapai pasangan
    (target_s1, target_s2) di mana perilaku penerimaan berbeda.

    Args:
        dfa1 (DFA): DFA pertama.
        dfa2 (DFA): DFA kedua.
        target_s1 (str): State target DFA 1 yang ditemukan berbeda.
        target_s2 (str): State target DFA 2 yang ditemukan berbeda.

    Returns:
        str: String yang diterima oleh satu DFA tapi ditolak oleh yang lain.
    """
    queue = [(dfa1.start_state, dfa2.start_state, '')]
    visited = {(dfa1.start_state, dfa2.start_state)}

    while queue:
        curr1, curr2, path = queue.pop(0)
        in1 = curr1 in dfa1.accept_states
        in2 = curr2 in dfa2.accept_states

        if in1 != in2:
            return path if path else 'ε'

        for sym in sorted(dfa1.alphabet):
            n1 = dfa1.transitions.get(curr1, {}).get(sym, 'dead')
            n2 = dfa2.transitions.get(curr2, {}).get(sym, 'dead')
            if (n1, n2) not in visited:
                visited.add((n1, n2))
                queue.append((n1, n2, path + sym))

    return '(tidak ditemukan)'


def _dfa_summary(dfa):
    """
    Menghasilkan ringkasan informasi sebuah DFA untuk ditampilkan di UI.

    Args:
        dfa (DFA): DFA yang akan diringkas.

    Returns:
        dict: Ringkasan DFA.
    """
    return {
        'states': dfa.states,
        'alphabet': dfa.alphabet,
        'start_state': dfa.start_state,
        'accept_states': dfa.accept_states,
        'num_states': len(dfa.states),
        'num_transitions': sum(
            len(symbols) for symbols in dfa.transitions.values()
        )
    }
