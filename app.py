from flask import Flask, render_template, request, jsonify
from automata.dfa import DFA
from automata.nfa import NFA
from automata.regex_to_nfa import regex_to_nfa
from automata.minimizer import DFAMinimizer
from automata.equivalence import check_equivalence, get_equivalence_details

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# ── Fitur 1: DFA Simulator ──────────────────────────────────────────────────

@app.route('/api/dfa/validate', methods=['POST'])
def dfa_validate():
    """Endpoint untuk memvalidasi aturan DFA sebelum simulasi."""
    data = request.json
    try:
        dfa = DFA(
            states=data['states'],
            alphabet=data['alphabet'],
            transitions=data['transitions'],
            start_state=data['start_state'],
            accept_states=data['accept_states']
        )
        result = dfa.validate()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

        # Validasi aturan terlebih dahulu
        validation = dfa.validate()
        if not validation['valid']:
            return jsonify({
                'error': 'Aturan DFA tidak valid',
                'validation_errors': validation['errors']
            }), 400

        string = data['string']
        result = dfa.simulate_verbose(string)

        return jsonify({
            'accepted': result['accepted'],
            'result': result['result'],
            'path': result['path'],
            'history': result['history'],
            'final_state': result['final_state'],
            'message': f'String "{string}" {"diterima" if result["accepted"] else "ditolak"}'
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
            'message': f'String "{string}" {"diterima" if accepted else "ditolak"}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ── Fitur 3: Minimisasi DFA ─────────────────────────────────────────────────

@app.route('/api/dfa/minimize', methods=['POST'])
def dfa_minimize():
    data = request.json
    try:
        minimizer = DFAMinimizer(
            states=data['states'],
            alphabet=data['alphabet'],
            transitions=data['transitions'],
            start_state=data['start_state'],
            accept_states=data['accept_states']
        )
        
        result = minimizer.minimize()
        
        if not result['success']:
            return jsonify({
                'error': 'Validasi DFA gagal',
                'validation_errors': result['error']
            }), 400

        stats = result['stats']

        return jsonify({
            'minimized': minimizer.to_dict(),
            'steps': result['iterations'],
            'distinguishable_table': result['distinguishable_table'],
            'merged_groups': result['merged_groups'],
            'original_states': stats['original_state_count'],
            'minimized_states': stats['minimal_state_count'],
            'message': f'Berhasil! Dari {stats["original_state_count"]} state → {stats["minimal_state_count"]} state'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# ── Fitur 4: Ekuivalensi DFA ────────────────────────────────────────────────

@app.route('/api/dfa/equivalence', methods=['POST'])
def dfa_equivalence():
    """
    Endpoint untuk memeriksa ekuivalensi dua DFA.

    Menerima JSON body:
      {
        "dfa1": { states, alphabet, transitions, start_state, accept_states },
        "dfa2": { states, alphabet, transitions, start_state, accept_states }
      }

    Mengembalikan:
      - equivalent    : bool
      - reason        : str   — penjelasan hasil
      - witness       : str | null — string pembeda (jika tidak ekuivalen)
      - steps         : list  — langkah-langkah product construction
      - visited_pairs : list  — pasangan state yang dikunjungi
      - dfa1_info     : dict  — ringkasan DFA 1
      - dfa2_info     : dict  — ringkasan DFA 2
    """
    data = request.json
    try:
        # Bangun kedua DFA
        dfa1 = DFA(
            states=data['dfa1']['states'],
            alphabet=data['dfa1']['alphabet'],
            transitions=data['dfa1']['transitions'],
            start_state=data['dfa1']['start_state'],
            accept_states=data['dfa1']['accept_states']
        )
        dfa2 = DFA(
            states=data['dfa2']['states'],
            alphabet=data['dfa2']['alphabet'],
            transitions=data['dfa2']['transitions'],
            start_state=data['dfa2']['start_state'],
            accept_states=data['dfa2']['accept_states']
        )

        # Validasi kedua DFA
        v1 = dfa1.validate()
        v2 = dfa2.validate()
        errors = []
        if not v1['valid']:
            errors.append(f'DFA 1 tidak valid: {"; ".join(v1["errors"])}')
        if not v2['valid']:
            errors.append(f'DFA 2 tidak valid: {"; ".join(v2["errors"])}')
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400

        # Jalankan pemeriksaan ekuivalensi detail
        details = get_equivalence_details(dfa1, dfa2)

        return jsonify({
            'equivalent': details['is_equivalent'],
            'reason': details['reason'],
            'witness': details['witness'],
            'steps': details['steps'],
            'visited_pairs': details['visited_pairs'],
            'dfa1_info': details['dfa1_info'],
            'dfa2_info': details['dfa2_info'],
            'message': f'Kedua DFA {"EKUIVALEN" if details["is_equivalent"] else "TIDAK EKUIVALEN"}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
