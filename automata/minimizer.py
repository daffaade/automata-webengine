from itertools import combinations
from collections import defaultdict


class DFAMinimizer:
    """
    Kelas DFA Minimizer — Implementasi Algoritma Table-Filling (Myhill-Nerode).

    Menerima komponen formal DFA yang sama dengan kelas DFA:
      - states        : list[str]  — himpunan status (Q)
      - alphabet      : list[str]  — himpunan simbol input (Σ)
      - transitions   : dict       — fungsi transisi (δ), format nested atau flat
      - start_state   : str        — status awal (q0)
      - accept_states : list[str]  — himpunan status akhir (F)

    Pipeline minimasi:
      1. validate()                 — validasi kelengkapan & kebenaran DFA
      2. remove_unreachable()       — hapus state yang tidak terjangkau
      3. build_distinguishable_table() — tandai pasangan yang dapat dibedakan
      4. merge_equivalent_states()  — gabungkan state yang ekuivalen
      5. minimize()                 — jalankan seluruh pipeline & kembalikan hasil

    Kompatibel dengan format input/output yang digunakan oleh kelas DFA.
    """

    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states        = list(states)
        self.alphabet      = list(alphabet)
        self.transitions   = self._normalize_transitions(transitions)
        self.start_state   = start_state
        self.accept_states = list(accept_states)

        # Akan diisi setelah minimize() dipanggil
        self._minimal_states       = None
        self._minimal_transitions  = None
        self._minimal_start        = None
        self._minimal_accepts      = None
        self._table                = None
        self._iterations           = None
        self._merged_groups        = None
        self._state_mapping        = None
        self._removed_unreachable  = []

    # ── Normalisasi Transisi ─────────────────────────────────────────────────

    def _normalize_transitions(self, transitions):
        """
        Normalisasi format transisi menjadi nested dictionary
        { state: { symbol: next_state } }.

        Mendukung dua format input:
          1. Sudah berupa dict of dict  → langsung dikembalikan.
          2. Format flat "state,symbol": next_state → dikonversi.
        """
        if not transitions:
            return {}

        first_key = next(iter(transitions))
        if isinstance(transitions[first_key], dict):
            return dict(transitions)

        result = {}
        for key, val in transitions.items():
            parts = key.split(',', 1)
            if len(parts) == 2:
                state, symbol = parts
                if state not in result:
                    result[state] = {}
                result[state][symbol] = val
        return result

    # ── Helper: index-based pair key ────────────────────────────────────────

    def _pair_key(self, a, b, states):
        """Kembalikan pasangan (qi, qj) dengan qi ≤ qj berdasarkan urutan states."""
        ia, ib = states.index(a), states.index(b)
        return (states[min(ia, ib)], states[max(ia, ib)])

    # ── 1. Validasi DFA ──────────────────────────────────────────────────────

    def validate(self):
        """
        Memvalidasi keabsahan aturan mesin DFA.

        Pemeriksaan yang dilakukan:
          1. Start state harus terdaftar di states.
          2. Setiap accept state harus terdaftar di states.
          3. Setiap state sumber & tujuan di transitions harus ada di states.
          4. Setiap simbol di transitions harus ada di alphabet.
          5. Kelengkapan: setiap (state, symbol) harus punya transisi terdefinisi.

        Returns:
            dict: { 'valid': bool, 'errors': list[str] }
        """
        errors = []

        # 1. Start state
        if self.start_state not in self.states:
            errors.append(
                f'Start state "{self.start_state}" tidak terdaftar '
                f'di dalam himpunan states {self.states}.'
            )

        # 2. Accept states
        for s in self.accept_states:
            if s not in self.states:
                errors.append(
                    f'Accept state "{s}" tidak terdaftar '
                    f'di dalam himpunan states {self.states}.'
                )

        # 3 & 4. Validasi transisi
        for src, sym_map in self.transitions.items():
            if src not in self.states:
                errors.append(
                    f'State sumber "{src}" pada fungsi transisi '
                    f'tidak terdaftar di dalam states.'
                )
            for sym, dst in sym_map.items():
                if sym not in self.alphabet:
                    errors.append(
                        f'Simbol "{sym}" pada delta({src}, {sym}) '
                        f'tidak terdaftar di dalam alphabet {self.alphabet}.'
                    )
                if dst not in self.states:
                    errors.append(
                        f'State tujuan "{dst}" pada delta({src}, {sym}) = {dst} '
                        f'tidak terdaftar di dalam himpunan states.'
                    )

        # 5. Kelengkapan transisi (DFA harus total)
        for state in self.states:
            for sym in self.alphabet:
                if state not in self.transitions or sym not in self.transitions[state]:
                    errors.append(
                        f'Transisi delta({state}, {sym}) tidak terdefinisi. '
                        f'DFA harus memiliki fungsi transisi yang total.'
                    )

        return {'valid': len(errors) == 0, 'errors': errors}

    # ── 2. Hapus Unreachable States ──────────────────────────────────────────

    def remove_unreachable(self):
        """
        Menghapus state yang tidak dapat dicapai dari start_state
        menggunakan BFS/DFS traversal.

        Menyimpan daftar state yang dihapus di self._removed_unreachable
        dan memperbarui self.states, self.transitions, self.accept_states
        secara in-place agar pipeline berikutnya bekerja pada set yang bersih.

        Returns:
            list[str]: State-state yang dihapus (unreachable).
        """
        reachable = set()
        queue = [self.start_state]
        while queue:
            state = queue.pop()
            if state in reachable:
                continue
            reachable.add(state)
            for sym in self.alphabet:
                nxt = self.transitions.get(state, {}).get(sym)
                if nxt and nxt not in reachable:
                    queue.append(nxt)

        removed = [s for s in self.states if s not in reachable]
        self._removed_unreachable = removed

        # Perbarui komponen DFA
        self.states        = [s for s in self.states if s in reachable]
        self.transitions   = {s: self.transitions[s] for s in self.states}
        self.accept_states = [s for s in self.accept_states if s in reachable]

        return removed

    # ── 3. Algoritma Table-Filling (Myhill-Nerode) ───────────────────────────

    def build_distinguishable_table(self):
        """
        Membangun tabel distinguishability menggunakan algoritma table-filling.

        Langkah basis:
          - Pasangan (accept, non-accept) langsung ditandai distinguishable.

        Langkah induksi (iterasi sampai tidak ada perubahan):
          - Pasangan (p, q) ditandai distinguishable jika terdapat simbol 'a'
            sehingga (δ(p,a), δ(q,a)) sudah ditandai distinguishable.

        Menyimpan hasil di:
          - self._table      : dict {(qi, qj): bool} — True = distinguishable
          - self._iterations : list[dict] — log tiap iterasi untuk frontend

        Returns:
            dict: { 'table': self._table, 'iterations': self._iterations }
        """
        states      = self.states
        alphabet    = self.alphabet
        transitions = self.transitions
        accepts     = set(self.accept_states)

        pairs = list(combinations(states, 2))
        table = {pair: False for pair in pairs}

        # Langkah basis
        for (p, q) in pairs:
            if (p in accepts) != (q in accepts):
                table[(p, q)] = True

        # Langkah induksi
        iterations  = []
        changed     = True
        iter_num    = 0

        while changed:
            changed      = False
            iter_num    += 1
            newly_marked = []

            for (p, q) in pairs:
                if table[(p, q)]:
                    continue
                for sym in alphabet:
                    r   = transitions[p][sym]
                    s   = transitions[q][sym]
                    if r == s:
                        continue
                    key = self._pair_key(r, s, states)
                    if table[key]:
                        table[(p, q)] = True
                        changed        = True
                        newly_marked.append({
                            'pair'       : [p, q],
                            'via_symbol' : sym,
                            'leads_to'   : [r, s]
                        })
                        break

            iterations.append({
                'iteration'           : iter_num,
                'newly_marked_pairs'  : newly_marked
            })

        self._table      = table
        self._iterations = iterations
        return {'table': table, 'iterations': iterations}

    # ── 4. Gabungkan Equivalent States (Union-Find) ──────────────────────────

    def merge_equivalent_states(self):
        """
        Menggabungkan state-state yang indistinguishable (ekuivalen) menjadi
        satu representatif menggunakan algoritma Union-Find dengan path compression.

        Prasyarat: build_distinguishable_table() sudah dipanggil.

        Setelah pemanggilan, properti berikut tersedia:
          - self._minimal_states      : list[str]
          - self._minimal_transitions : dict[str, dict[str, str]]
          - self._minimal_start       : str
          - self._minimal_accepts     : list[str]
          - self._merged_groups       : dict[str, list[str]]  # {rep: [anggota]}
          - self._state_mapping       : dict[str, str]        # {state_asli: rep}

        Returns:
            dict: Komponen DFA minimal (tanpa merged_groups & state_mapping).
        """
        if self._table is None:
            raise RuntimeError(
                'Panggil build_distinguishable_table() terlebih dahulu.'
            )

        states      = self.states
        transitions = self.transitions
        accepts     = set(self.accept_states)
        table       = self._table

        # Union-Find
        parent = {s: s for s in states}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                # Representatif = state dengan indeks lebih kecil di list states
                if states.index(rx) > states.index(ry):
                    rx, ry = ry, rx
                parent[ry] = rx

        for (p, q) in combinations(states, 2):
            key = self._pair_key(p, q, states)
            if not table[key]:
                union(p, q)

        # Pemetaan state → representatif
        state_to_rep = {s: find(s) for s in states}

        # Kumpulkan representatif unik (pertahankan urutan asli)
        seen       = []
        for s in states:
            r = find(s)
            if r not in seen:
                seen.append(r)
        new_states = seen

        # Bangun transisi DFA minimal
        new_transitions = {}
        for rep in new_states:
            new_transitions[rep] = {}
            for sym in self.alphabet:
                target                    = transitions[rep][sym]
                new_transitions[rep][sym] = find(target)

        new_start   = find(self.start_state)
        new_accepts = [s for s in new_states if s in {find(a) for a in accepts}]

        # Kelompok gabungan (hanya yang > 1 anggota relevan untuk ditampilkan)
        groups = defaultdict(list)
        for s in states:
            groups[find(s)].append(s)

        # Simpan ke instance
        self._minimal_states      = new_states
        self._minimal_transitions = new_transitions
        self._minimal_start       = new_start
        self._minimal_accepts     = new_accepts
        self._merged_groups       = dict(groups)
        self._state_mapping       = state_to_rep

        return {
            'states'       : new_states,
            'alphabet'     : self.alphabet,
            'transitions'  : new_transitions,
            'start_state'  : new_start,
            'accept_states': new_accepts,
        }

    # ── 5. Pipeline Utama ────────────────────────────────────────────────────

    def minimize(self):
        """
        Menjalankan seluruh pipeline minimasi DFA secara berurutan:
          1. validate()
          2. remove_unreachable()
          3. build_distinguishable_table()
          4. merge_equivalent_states()

        Returns:
            dict: Hasil lengkap siap dikonsumsi oleh route Flask/FastAPI.
            {
                'success'               : bool,
                'error'                 : str | None,
                'original_dfa'          : dict,       ← DFA setelah hapus unreachable
                'minimal_dfa'           : dict,       ← DFA hasil minimasi
                'distinguishable_table' : list[dict], ← tabel pasangan + status
                'iterations'            : list[dict], ← log tiap iterasi
                'merged_groups'         : dict,       ← {rep: [state...]} (hanya yang > 1)
                'state_mapping'         : dict,       ← {state_asli: rep}
                'stats'                 : dict        ← ringkasan statistik
            }
        """
        original_count = len(self.states)

        # 1. Validasi
        val = self.validate()
        if not val['valid']:
            return {
                'success': False,
                'error'  : val['errors'],
                'minimal_dfa': None,
                'stats'  : None
            }

        # Simpan snapshot DFA original (sebelum dimodifikasi)
        original_snapshot = {
            'states'       : list(self.states),
            'alphabet'     : list(self.alphabet),
            'transitions'  : {s: dict(t) for s, t in self.transitions.items()},
            'start_state'  : self.start_state,
            'accept_states': list(self.accept_states),
        }

        # 2. Hapus unreachable
        self.remove_unreachable()

        after_unreachable_count = len(self.states)

        # 3. Table-filling
        self.build_distinguishable_table()

        # 4. Merge equivalent
        minimal_components = self.merge_equivalent_states()

        # Format tabel untuk JSON output
        table_readable = [
            {
                'pair'            : list(pair),
                'distinguishable' : is_dist
            }
            for pair, is_dist in self._table.items()
        ]

        # Hanya tampilkan grup yang benar-benar digabung (> 1 anggota)
        meaningful_groups = {
            rep: members
            for rep, members in self._merged_groups.items()
            if len(members) > 1
        }

        stats = {
            'original_state_count'      : original_count,
            'after_remove_unreachable'  : after_unreachable_count,
            'minimal_state_count'       : len(self._minimal_states),
            'removed_unreachable'       : self._removed_unreachable,
            'states_reduced_by'         : original_count - len(self._minimal_states),
            'is_already_minimal'        : len(self._minimal_states) == after_unreachable_count,
        }

        return {
            'success'               : True,
            'error'                 : None,
            'original_dfa'          : original_snapshot,
            'minimal_dfa'           : minimal_components,
            'distinguishable_table' : table_readable,
            'iterations'            : self._iterations,
            'merged_groups'         : meaningful_groups,
            'state_mapping'         : self._state_mapping,
            'stats'                 : stats,
        }

    # ── Serialisasi ──────────────────────────────────────────────────────────

    def to_dict(self):
        """
        Konversi DFA minimal ke format dict flat ("state,symbol": next_state)
        agar kompatibel dengan format yang digunakan kelas DFA.

        Prasyarat: minimize() sudah dipanggil.

        Returns:
            dict: Representasi DFA minimal siap dimasukkan ke kelas DFA.
        """
        if self._minimal_states is None:
            raise RuntimeError('Panggil minimize() terlebih dahulu.')

        flat_trans = {}
        for state, syms in self._minimal_transitions.items():
            for sym, nxt in syms.items():
                flat_trans[f'{state},{sym}'] = nxt

        return {
            'states'       : self._minimal_states,
            'alphabet'     : self.alphabet,
            'transitions'  : flat_trans,
            'start_state'  : self._minimal_start,
            'accept_states': self._minimal_accepts,
        }

    def get_graph_data(self):
        """
        Format data DFA minimal untuk visualisasi Cytoscape.js.
        Kompatibel dengan method get_graph_data() pada kelas DFA.

        Prasyarat: minimize() sudah dipanggil.

        Returns:
            list[dict]: Gabungan nodes dan edges dalam format Cytoscape.
        """
        if self._minimal_states is None:
            raise RuntimeError('Panggil minimize() terlebih dahulu.')

        nodes = []
        for state in self._minimal_states:
            cls = 'state'
            if state in self._minimal_accepts:
                cls += ' accept'
            if state == self._minimal_start:
                cls += ' start'
            nodes.append({
                'data'   : {'id': state, 'label': state},
                'classes': cls
            })

        edge_map = {}
        for state, syms in self._minimal_transitions.items():
            for sym, nxt in syms.items():
                key = f'{state}->{nxt}'
                if key not in edge_map:
                    edge_map[key] = {'source': state, 'target': nxt, 'labels': []}
                edge_map[key]['labels'].append(sym)

        edges = []
        for key, edge in edge_map.items():
            edges.append({
                'data': {
                    'id'    : key,
                    'source': edge['source'],
                    'target': edge['target'],
                    'label' : ', '.join(edge['labels'])
                }
            })

        return nodes + edges