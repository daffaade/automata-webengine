class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        # transitions: dict dengan key "state,symbol" → next_state
        # atau dict of dict: {state: {symbol: next_state}}
        self.transitions = self._normalize_transitions(transitions)
        self.start_state = start_state
        self.accept_states = accept_states

    def _normalize_transitions(self, transitions):
        """Normalisasi format transisi menjadi dict of dict"""
        if not transitions:
            return {}
        # Jika sudah dict of dict
        first_key = next(iter(transitions))
        if isinstance(first_key, str) and ',' not in first_key:
            return transitions
        # Jika format "state,symbol": next_state
        result = {}
        for key, val in transitions.items():
            parts = key.split(',', 1)
            if len(parts) == 2:
                state, symbol = parts
                if state not in result:
                    result[state] = {}
                result[state][symbol] = val
        return result

    def simulate(self, input_string):
        """
        Jalankan DFA pada input_string.
        Return: (accepted: bool, path: list of states)
        """
        current = self.start_state
        path = [current]

        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f'Simbol "{symbol}" tidak ada dalam alphabet')
            trans = self.transitions.get(current, {})
            if symbol not in trans:
                # Dead state / trap state
                return False, path
            current = trans[symbol]
            path.append(current)

        accepted = current in self.accept_states
        return accepted, path

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