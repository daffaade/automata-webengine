from automata.nfa import NFA, EPSILON

class NFAFragment:
    """Fragment NFA kecil dalam proses Thompson's construction"""
    _counter = 0

    def __init__(self, start, accept, transitions):
        self.start = start
        self.accept = accept
        self.transitions = transitions  # {state: {symbol: [states]}}

    @staticmethod
    def new_state():
        NFAFragment._counter += 1
        return f'q{NFAFragment._counter}'

    @staticmethod
    def reset():
        NFAFragment._counter = 0

def add_transition(transitions, from_state, symbol, to_state):
    if from_state not in transitions:
        transitions[from_state] = {}
    if symbol not in transitions[from_state]:
        transitions[from_state][symbol] = []
    if to_state not in transitions[from_state][symbol]:
        transitions[from_state][symbol].append(to_state)

def merge_transitions(*trans_list):
    """Gabungkan beberapa dict transisi"""
    result = {}
    for trans in trans_list:
        for state, symbols in trans.items():
            if state not in result:
                result[state] = {}
            for symbol, targets in symbols.items():
                if symbol not in result[state]:
                    result[state][symbol] = []
                for t in targets:
                    if t not in result[state][symbol]:
                        result[state][symbol].append(t)
    return result

def build_symbol(symbol):
    """NFA untuk satu simbol: q0 --(symbol)--> q1"""
    s0 = NFAFragment.new_state()
    s1 = NFAFragment.new_state()
    trans = {}
    add_transition(trans, s0, symbol, s1)
    return NFAFragment(s0, s1, trans)

def build_concat(frag1, frag2):
    """Konkatenasi: frag1 lalu frag2"""
    trans = merge_transitions(frag1.transitions, frag2.transitions)
    add_transition(trans, frag1.accept, EPSILON, frag2.start)
    return NFAFragment(frag1.start, frag2.accept, trans)

def build_union(frag1, frag2):
    """Union (alternasi): frag1 | frag2"""
    s0 = NFAFragment.new_state()
    s1 = NFAFragment.new_state()
    trans = merge_transitions(frag1.transitions, frag2.transitions)
    add_transition(trans, s0, EPSILON, frag1.start)
    add_transition(trans, s0, EPSILON, frag2.start)
    add_transition(trans, frag1.accept, EPSILON, s1)
    add_transition(trans, frag2.accept, EPSILON, s1)
    return NFAFragment(s0, s1, trans)

def build_kleene(frag):
    """Kleene star: frag*"""
    s0 = NFAFragment.new_state()
    s1 = NFAFragment.new_state()
    trans = merge_transitions(frag.transitions)
    add_transition(trans, s0, EPSILON, frag.start)
    add_transition(trans, s0, EPSILON, s1)
    add_transition(trans, frag.accept, EPSILON, frag.start)
    add_transition(trans, frag.accept, EPSILON, s1)
    return NFAFragment(s0, s1, trans)

def build_plus(frag):
    """Plus: frag+ (satu atau lebih) — NOTE: Dalam konteks TBA, + biasanya berarti union.
    Fungsi ini tetap tersedia jika diperlukan untuk notasi regex standar."""
    s0 = NFAFragment.new_state()
    s1 = NFAFragment.new_state()
    trans = merge_transitions(frag.transitions)
    add_transition(trans, s0, EPSILON, frag.start)
    add_transition(trans, frag.accept, EPSILON, frag.start)
    add_transition(trans, frag.accept, EPSILON, s1)
    return NFAFragment(s0, s1, trans)

def build_optional(frag):
    """Optional: frag? (nol atau satu)"""
    s0 = NFAFragment.new_state()
    s1 = NFAFragment.new_state()
    trans = merge_transitions(frag.transitions)
    add_transition(trans, s0, EPSILON, frag.start)
    add_transition(trans, s0, EPSILON, s1)
    add_transition(trans, frag.accept, EPSILON, s1)
    return NFAFragment(s0, s1, trans)

class RegexParser:
    """Parser regex dengan precedence: * > concat > |/+
    Catatan: '+' diperlakukan sebagai UNION (alternasi), bukan quantifier.
    Ini sesuai dengan konvensi TBA (Teori Bahasa & Automata)."""

    def __init__(self, regex):
        self.regex = regex
        self.pos = 0

    def peek(self):
        return self.regex[self.pos] if self.pos < len(self.regex) else None

    def consume(self):
        ch = self.regex[self.pos]
        self.pos += 1
        return ch

    def parse(self):
        """Parse expression (level terbawah: union)"""
        return self.parse_union()

    def parse_union(self):
        left = self.parse_concat()
        while self.peek() in ('|', '+'):
            self.consume()
            right = self.parse_concat()
            left = build_union(left, right)
        return left

    def parse_concat(self):
        left = self.parse_quantifier()
        while self.peek() and self.peek() not in ('|', '+', ')'):
            right = self.parse_quantifier()
            left = build_concat(left, right)
        return left

    def parse_quantifier(self):
        frag = self.parse_atom()
        while self.peek() in ('*', '?'):
            op = self.consume()
            if op == '*':
                frag = build_kleene(frag)
            elif op == '?':
                frag = build_optional(frag)
        return frag

    def parse_atom(self):
        ch = self.peek()
        if ch == '(':
            self.consume()
            frag = self.parse_union()
            if self.peek() == ')':
                self.consume()
            return frag
        elif ch == '\\':
            self.consume()
            escaped = self.consume()
            return build_symbol(escaped)
        elif ch and ch not in ('|', '+', ')', '*', '?'):
            self.consume()
            return build_symbol(ch)
        else:
            raise ValueError(f'Karakter tidak terduga di posisi {self.pos}: "{ch}"')

def regex_to_nfa(regex):
    """
    Konversi regex ke NFA menggunakan Thompson's construction.
    Return: NFA object
    """
    if not regex:
        raise ValueError('Regex tidak boleh kosong')

    NFAFragment.reset()
    parser = RegexParser(regex)
    frag = parser.parse()

    if parser.pos != len(regex):
        raise ValueError(f'Regex tidak valid: karakter tidak terbaca di posisi {parser.pos}')

    # Kumpulkan semua state
    all_states = set()
    for state, symbols in frag.transitions.items():
        all_states.add(state)
        for targets in symbols.values():
            all_states.update(targets)
    all_states.add(frag.start)
    all_states.add(frag.accept)

    # Kumpulkan alphabet (tanpa epsilon)
    alphabet = set()
    for symbols in frag.transitions.values():
        for sym in symbols:
            if sym != EPSILON:
                alphabet.add(sym)

    return NFA(
        states=sorted(list(all_states), key=lambda x: int(x[1:]) if x.startswith('q') and x[1:].isdigit() else 0),
        alphabet=sorted(list(alphabet)),
        transitions=frag.transitions,
        start_state=frag.start,
        accept_states=[frag.accept]
    )