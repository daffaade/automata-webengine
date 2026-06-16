class DFA:
    """
    Kelas DFA Universal — Blueprint Matematika 5-tuple.

    Menerima komponen formal DFA:
      - states        : list[str]  — himpunan status (Q)
      - alphabet      : list[str]  — himpunan simbol input (Σ)
      - transitions    : dict       — fungsi transisi (δ)
      - start_state   : str        — status awal (q0)
      - accept_states : list[str]  — himpunan status akhir (F)

    Fungsi transisi disimpan secara internal sebagai nested dictionary:
        { current_state: { input_character: next_state } }
    """

    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        # transitions: dict dengan key "state,symbol" → next_state
        # atau dict of dict: {state: {symbol: next_state}}
        self.transitions = self._normalize_transitions(transitions)
        self.start_state = start_state
        self.accept_states = accept_states

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

        # Cek apakah value dari key pertama adalah dict (sudah nested)
        if isinstance(transitions[first_key], dict):
            return transitions

        # Format flat "state,symbol" → next_state
        result = {}
        for key, val in transitions.items():
            parts = key.split(',', 1)
            if len(parts) == 2:
                state, symbol = parts
                if state not in result:
                    result[state] = {}
                result[state][symbol] = val
        return result

    # ── Validasi Aturan Deterministik ────────────────────────────────────────

    def validate(self):
        """
        Memvalidasi keabsahan aturan mesin DFA yang dimasukkan pengguna.

        Pemeriksaan yang dilakukan:
          1. Start State harus merupakan bagian sah dari himpunan States.
          2. Seluruh elemen di dalam Accept States harus bagian sah dari States.
          3. Setiap status sumber dan status tujuan di dalam fungsi transisi
             harus terdaftar di dalam himpunan States.
          4. Setiap simbol di dalam fungsi transisi harus terdaftar di dalam
             himpunan Alphabet.
          5. Sifat deterministik: setiap pasangan (state, symbol) hanya
             menunjuk tepat ke satu status berikutnya (dijamin oleh struktur
             dictionary — tidak perlu pengecekan duplikat eksplisit).

        Returns:
            dict: { 'valid': bool, 'errors': list[str] }
        """
        errors = []

        # 1. Validasi Start State
        if self.start_state not in self.states:
            errors.append(
                f'Start state "{self.start_state}" tidak terdaftar '
                f'di dalam himpunan states {self.states}.'
            )

        # 2. Validasi Accept States
        for state in self.accept_states:
            if state not in self.states:
                errors.append(
                    f'Accept state "{state}" tidak terdaftar '
                    f'di dalam himpunan states {self.states}.'
                )

        # 3 & 4. Validasi fungsi transisi
        for src_state, symbol_map in self.transitions.items():
            # Periksa status sumber
            if src_state not in self.states:
                errors.append(
                    f'Status sumber transisi "{src_state}" tidak terdaftar '
                    f'di dalam himpunan states.'
                )

            for symbol, dest_state in symbol_map.items():
                # Periksa simbol
                if symbol not in self.alphabet:
                    errors.append(
                        f'Simbol "{symbol}" pada transisi '
                        f'delta({src_state}, {symbol}) tidak terdaftar '
                        f'di dalam alphabet {self.alphabet}.'
                    )
                # Periksa status tujuan
                if dest_state not in self.states:
                    errors.append(
                        f'Status tujuan "{dest_state}" pada transisi '
                        f'delta({src_state}, {symbol}) = {dest_state} tidak '
                        f'terdaftar di dalam himpunan states.'
                    )

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    # ── Simulasi & Pelacakan Riwayat Status ──────────────────────────────────

    def simulate(self, input_string):
        """
        Menjalankan simulasi DFA pada string uji yang diberikan.

        Algoritma penelusuran:
          1. Inisialisasi current_state = start_state.
          2. Buat array history kosong untuk merekam jejak perpindahan.
          3. Loop membaca string karakter demi karakter:
             - Jika karakter ∉ alphabet atau tidak ada transisi terdefinisi
               → hentikan (break) dengan kesimpulan penolakan.
             - Jika transisi tersedia → perbarui current_state dan catat
               kronologi perpindahan ke history.
          4. Setelah semua karakter diproses, periksa apakah current_state
             ∈ accept_states.

        Args:
            input_string (str): String yang akan dievaluasi.

        Returns:
            tuple: (accepted: bool, path: list[str])
                - accepted : True jika string diterima, False jika ditolak.
                - path     : List status yang dilalui (termasuk start state),
                             kompatibel dengan kontrak yang digunakan oleh
                             app.py dan fitur-fitur lain (minimizer, dsb).

        Untuk mendapatkan hasil lengkap dengan state history terstruktur,
        gunakan method simulate_verbose().
        """
        current = self.start_state
        path = [current]

        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f'Simbol "{symbol}" tidak ada dalam alphabet')
            trans = self.transitions.get(current, {})
            if symbol not in trans:
                # Dead state / trap state — tidak ada rute transisi
                return False, path
            current = trans[symbol]
            path.append(current)

        accepted = current in self.accept_states
        return accepted, path

    def simulate_verbose(self, input_string):
        """
        Versi lengkap dari simulate() yang menghasilkan log transisi
        terstruktur (State History) untuk keperluan animasi visual frontend.

        Setiap entri di dalam history merekam:
          - current_state  : status sebelum perpindahan
          - symbol         : karakter yang dibaca
          - next_state     : status setelah perpindahan

        Returns:
            dict: Struktur kembalian siap diubah menjadi JSON oleh Flask.
                {
                    'accepted'     : bool,
                    'result'       : "Accepted" | "Rejected",
                    'final_state'  : str,
                    'history'      : list[dict],
                    'path'         : list[str],
                    'input_string' : str
                }
        """
        current = self.start_state
        path = [current]
        history = []
        rejected_early = False

        for symbol in input_string:
            # Periksa apakah simbol valid
            if symbol not in self.alphabet:
                history.append({
                    'current_state': current,
                    'symbol': symbol,
                    'next_state': None,
                    'error': f'Simbol "{symbol}" tidak ada dalam alphabet'
                })
                rejected_early = True
                break

            trans = self.transitions.get(current, {})

            # Periksa apakah transisi tersedia
            if symbol not in trans:
                history.append({
                    'current_state': current,
                    'symbol': symbol,
                    'next_state': None,
                    'error': f'Tidak ada transisi delta({current}, {symbol})'
                })
                rejected_early = True
                break

            # Transisi tersedia — lakukan perpindahan
            next_state = trans[symbol]
            history.append({
                'current_state': current,
                'symbol': symbol,
                'next_state': next_state
            })
            current = next_state
            path.append(current)

        # Tentukan hasil akhir
        if rejected_early:
            accepted = False
        else:
            accepted = current in self.accept_states

        return {
            'accepted': accepted,
            'result': 'Accepted' if accepted else 'Rejected',
            'final_state': current,
            'history': history,
            'path': path,
            'input_string': input_string
        }

    # ── Serialisasi ──────────────────────────────────────────────────────────

    def to_dict(self):
        """Konversi ke format dict untuk JSON response"""
        # Flatten transitions ke format "state,symbol": next_state
        flat_trans = {}
        for state, symbols in self.transitions.items():
            for symbol, next_state in symbols.items():
                flat_trans[f"{state},{symbol}"] = next_state

        return {
            'states': self.states,
            'alphabet': self.alphabet,
            'transitions': flat_trans,
            'start_state': self.start_state,
            'accept_states': self.accept_states
        }

    def get_graph_data(self):
        """Format data untuk visualisasi Cytoscape.js"""
        nodes = []
        for state in self.states:
            node_class = 'state'
            if state in self.accept_states:
                node_class += ' accept'
            if state == self.start_state:
                node_class += ' start'
            nodes.append({
                'data': {'id': state, 'label': state},
                'classes': node_class
            })

        edges = []
        edge_map = {}  # Gabung multiple transisi antara 2 state yang sama
        for state, symbols in self.transitions.items():
            for symbol, next_state in symbols.items():
                key = f"{state}->{next_state}"
                if key not in edge_map:
                    edge_map[key] = {'source': state, 'target': next_state, 'labels': []}
                edge_map[key]['labels'].append(symbol)

        for key, edge in edge_map.items():
            label = ', '.join(edge['labels'])
            edges.append({
                'data': {
                    'id': key,
                    'source': edge['source'],
                    'target': edge['target'],
                    'label': label
                }
            })

        return nodes + edges