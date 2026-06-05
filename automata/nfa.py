EPSILON = 'ε'

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        # transitions: {state: {symbol: [list of next states]}}
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def epsilon_closure(self, states):
        """Hitung ε-closure dari sekumpulan state"""
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            eps_moves = self.transitions.get(state, {}).get(EPSILON, [])
            for next_state in eps_moves:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return frozenset(closure)

    def move(self, states, symbol):
        """Hitung set state yang bisa dicapai dari states dengan symbol"""
        result = set()
        for state in states:
            next_states = self.transitions.get(state, {}).get(symbol, [])
            result.update(next_states)
        return result

    def simulate(self, input_string):
        """
        Jalankan NFA pada input_string menggunakan subset construction.
        Return: accepted (bool)
        """
        current_states = self.epsilon_closure({self.start_state})

        for symbol in input_string:
            if symbol not in self.alphabet and symbol != EPSILON:
                raise ValueError(f'Simbol "{symbol}" tidak ada dalam alphabet')
            moved = self.move(current_states, symbol)
            current_states = self.epsilon_closure(moved)

        return bool(current_states & set(self.accept_states))

    def to_dict(self):
        """Konversi ke format dict untuk JSON response dan visualisasi"""
        flat_trans = {}
        for state, symbols in self.transitions.items():
            for symbol, next_states in symbols.items():
                key = f"{state},{symbol}"
                flat_trans[key] = next_states

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
        edge_map = {}
        for state, symbols in self.transitions.items():
            for symbol, next_states in symbols.items():
                for next_state in next_states:
                    key = f"{state}-{symbol}->{next_state}"
                    edges.append({
                        'data': {
                            'id': key,
                            'source': state,
                            'target': next_state,
                            'label': symbol
                        },
                        'classes': 'epsilon' if symbol == EPSILON else ''
                    })

        return nodes + edges