from flask import Flask, render_template, request, jsonify
from automata.dfa import DFA
from automata.nfa import NFA
from automata.regex_to_nfa import regex_to_nfa
from automata.minimizer import minimize_dfa, check_equivalence

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# ── Fitur 1: DFA Simulator ──────────────────────────────────────────────────

@app.route('/api/dfa/test', methods=['POST'])
def dfa_test():
    data = request.json
    try:
        dfa = DFA(
            states=data['states'],
            alphabet=data['alphabet'],
            transitions=data['transitions'],
            start_state=data['start_state'],
            accept_states=data['accept_states']
        )
        string = data['string']
        accepted, path = dfa.simulate(string)
        return jsonify({
            'accepted': accepted,
            'path': path,
            'message': f'String "{string}" {"diterima ✓" if accepted else "ditolak ✗"}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ── Fitur 2: Regex → NFA ────────────────────────────────────────────────────

@app.route('/api/regex/to-nfa', methods=['POST'])
def regex_convert():
    data = request.json
    try:
        nfa = regex_to_nfa(data['regex'])
        nfa_data = nfa.to_dict()
        return jsonify({'nfa': nfa_data, 'message': 'NFA berhasil dibuat'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/nfa/test', methods=['POST'])
def nfa_test():
    data = request.json
    try:
        nfa = NFA(
            states=data['states'],
            alphabet=data['alphabet'],
            transitions=data['transitions'],
            start_state=data['start_state'],
            accept_states=data['accept_states']
        )
        string = data['string']
        accepted = nfa.simulate(string)
        return jsonify({
            'accepted': accepted,
            'message': f'String "{string}" {"diterima ✓" if accepted else "ditolak ✗"}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ── Fitur 3: Minimisasi DFA ─────────────────────────────────────────────────

@app.route('/api/dfa/minimize', methods=['POST'])
def dfa_minimize():
    data = request.json
    try:
        dfa = DFA(
            states=data['states'],
            alphabet=data['alphabet'],
            transitions=data['transitions'],
            start_state=data['start_state'],
            accept_states=data['accept_states']
        )
        min_dfa, steps = minimize_dfa(dfa)
        return jsonify({
            'minimized': min_dfa.to_dict(),
            'steps': steps,
            'original_states': len(dfa.states),
            'minimized_states': len(min_dfa.states),
            'message': f'Berhasil! Dari {len(dfa.states)} state → {len(min_dfa.states)} state'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ── Fitur 4: Ekuivalensi DFA ────────────────────────────────────────────────

@app.route('/api/dfa/equivalence', methods=['POST'])
def dfa_equivalence():
    data = request.json
    try:
        dfa1 = DFA(**data['dfa1'])
        dfa2 = DFA(**data['dfa2'])
        equivalent, reason = check_equivalence(dfa1, dfa2)
        return jsonify({
            'equivalent': equivalent,
            'reason': reason,
            'message': f'Kedua DFA {"EKUIVALEN ✓" if equivalent else "TIDAK EKUIVALEN ✗"}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
