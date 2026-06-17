// ═══ Tab Navigation ═══
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
    });
});

// ═══ Helpers ═══
function parseList(val) { return val.split(',').map(s => s.trim()).filter(Boolean); }

function parseTransitions(text) {
    const trans = {};
    text.split('\n').forEach(line => {
        line = line.trim();
        if (!line) return;
        const [left, right] = line.split('=');
        if (left && right) trans[left.trim()] = right.trim();
    });
    return trans;
}

function showResult(panelId, success, headerText, bodyHTML) {
    const panel = document.getElementById(panelId);
    const header = document.getElementById(panelId + '-header');
    const body = document.getElementById(panelId + '-body');
    panel.classList.remove('hidden');
    header.className = 'result-header ' + (success ? 'success' : 'error');
    header.textContent = (success ? '\u2714 ' : '\u2718 ') + headerText;
    body.innerHTML = bodyHTML;
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showLoading(panelId, msg) {
    const panel = document.getElementById(panelId);
    const header = document.getElementById(panelId + '-header');
    const body = document.getElementById(panelId + '-body');
    panel.classList.remove('hidden');
    header.className = 'result-header';
    header.innerHTML = '<span class="spinner"></span> ' + (msg || 'Memproses...');
    body.innerHTML = '';
}

function buildPathHTML(path, acceptStates) {
    return '<div class="path-display">' +
        path.map((s, i) => {
            let cls = 'path-state';
            if (i === path.length - 1) cls += acceptStates && acceptStates.includes(s) ? ' accept' : ' reject';
            const arrow = i < path.length - 1 ? '<span class="path-arrow">\u2192</span>' : '';
            return '<span class="' + cls + '">' + s + '</span>' + arrow;
        }).join('') +
        '</div>';
}

// ═══ Tab 1: DFA Simulator ═══
async function testDFA() {
    const data = {
        states: parseList(document.getElementById('dfa-sim-states').value),
        alphabet: parseList(document.getElementById('dfa-sim-alphabet').value),
        transitions: parseTransitions(document.getElementById('dfa-sim-transitions').value),
        start_state: document.getElementById('dfa-sim-start').value.trim(),
        accept_states: parseList(document.getElementById('dfa-sim-accept').value),
        string: document.getElementById('dfa-sim-string').value
    };
    showLoading('result-dfa-sim', 'Mensimulasikan DFA...');
    try {
        const res = await fetch('/api/dfa/test', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || 'Gagal');
        let body = '<h4>Path</h4>' + buildPathHTML(json.path, data.accept_states);
        body += '<h4>History</h4>';
        json.history.forEach(h => {
            body += '<div class="step-item"><span class="step-desc">\u03B4(' + h.current_state + ', ' + h.symbol + ') = ' + (h.next_state || 'undefined') + '</span></div>';
        });
        body += '<h4>Final State</h4><p style="font-family:var(--font-mono)">' + json.final_state + '</p>';
        showResult('result-dfa-sim', json.accepted, json.message, body);
    } catch (e) { showResult('result-dfa-sim', false, 'Error', '<p>' + e.message + '</p>'); }
}

// ═══ Tab 2: Regex → NFA ═══
let currentNFA = null;
async function convertRegex() {
    const regex = document.getElementById('regex-input').value.trim();
    if (!regex) return;
    showLoading('result-regex', 'Mengonversi Regex ke NFA...');
    try {
        const res = await fetch('/api/regex/to-nfa', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({regex}) });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || 'Gagal');
        currentNFA = json.nfa;
        let body = '<h4>States</h4><p class="nfa-detail-item">' + json.nfa.states.join(', ') + '</p>';
        body += '<h4>Alphabet</h4><p class="nfa-detail-item">' + json.nfa.alphabet.join(', ') + '</p>';
        body += '<h4>Start State</h4><p class="nfa-detail-item">' + json.nfa.start_state + '</p>';
        body += '<h4>Accept States</h4><p class="nfa-detail-item">' + json.nfa.accept_states.join(', ') + '</p>';
        body += '<h4>Transisi</h4>';
        Object.entries(json.nfa.transitions).forEach(([k, v]) => {
            body += '<div class="nfa-detail-item">\u03B4(' + k.replace(',', ', ') + ') = {' + (Array.isArray(v) ? v.join(', ') : v) + '}</div>';
        });
        showResult('result-regex', true, json.message, body);
        document.getElementById('nfa-test-section').classList.remove('hidden');
    } catch (e) { showResult('result-regex', false, 'Error', '<p>' + e.message + '</p>'); }
}

async function testNFA() {
    if (!currentNFA) return;
    const str = document.getElementById('nfa-test-string').value;
    showLoading('result-nfa-test', 'Menguji string pada NFA...');
    try {
        const payload = { ...currentNFA, string: str };
        const res = await fetch('/api/nfa/test', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || 'Gagal');
        showResult('result-nfa-test', json.accepted, json.message, '');
    } catch (e) { showResult('result-nfa-test', false, 'Error', '<p>' + e.message + '</p>'); }
}

// ═══ Tab 3: Minimisasi DFA ═══
async function minimizeDFA() {
    const data = {
        states: parseList(document.getElementById('dfa-min-states').value),
        alphabet: parseList(document.getElementById('dfa-min-alphabet').value),
        transitions: parseTransitions(document.getElementById('dfa-min-transitions').value),
        start_state: document.getElementById('dfa-min-start').value.trim(),
        accept_states: parseList(document.getElementById('dfa-min-accept').value)
    };
    showLoading('result-dfa-min', 'Meminimisasi DFA...');
    try {
        const res = await fetch('/api/dfa/minimize', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || 'Gagal');
        let body = '<div class="info-grid"><div class="info-box"><div class="info-label">State Awal</div><div class="info-value">' + json.original_states + '</div></div>';
        body += '<div class="info-box"><div class="info-label">State Minimal</div><div class="info-value">' + json.minimized_states + '</div></div></div>';
        body += '<h4>Langkah Minimisasi</h4>';
        json.steps.forEach(s => {
            body += '<div class="step-item"><div class="step-label">Langkah ' + s.step + '</div><div class="step-desc">' + s.description + '</div>';
            if (s.partitions) body += '<div class="step-detail">Partisi: ' + JSON.stringify(s.partitions) + '</div>';
            body += '</div>';
        });
        body += '<h4>DFA Minimal</h4>';
        body += '<p class="nfa-detail-item">States: ' + json.minimized.states.join(', ') + '</p>';
        body += '<p class="nfa-detail-item">Start: ' + json.minimized.start_state + '</p>';
        body += '<p class="nfa-detail-item">Accept: ' + json.minimized.accept_states.join(', ') + '</p>';
        Object.entries(json.minimized.transitions).forEach(([k, v]) => {
            body += '<div class="nfa-detail-item">\u03B4(' + k.replace(',', ', ') + ') = ' + v + '</div>';
        });
        showResult('result-dfa-min', true, json.message, body);
    } catch (e) { showResult('result-dfa-min', false, 'Error', '<p>' + e.message + '</p>'); }
}

// ═══ Tab 4: Ekuivalensi DFA ═══
async function checkEquivalence() {
    const dfa1 = {
        states: parseList(document.getElementById('eq-dfa1-states').value),
        alphabet: parseList(document.getElementById('eq-dfa1-alphabet').value),
        transitions: parseTransitions(document.getElementById('eq-dfa1-transitions').value),
        start_state: document.getElementById('eq-dfa1-start').value.trim(),
        accept_states: parseList(document.getElementById('eq-dfa1-accept').value)
    };
    const dfa2 = {
        states: parseList(document.getElementById('eq-dfa2-states').value),
        alphabet: parseList(document.getElementById('eq-dfa2-alphabet').value),
        transitions: parseTransitions(document.getElementById('eq-dfa2-transitions').value),
        start_state: document.getElementById('eq-dfa2-start').value.trim(),
        accept_states: parseList(document.getElementById('eq-dfa2-accept').value)
    };
    showLoading('result-equiv', 'Memeriksa ekuivalensi...');
    try {
        const res = await fetch('/api/dfa/equivalence', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dfa1, dfa2 })
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || 'Gagal');

        let body = '';

        // Info kedua DFA
        if (json.dfa1_info && json.dfa2_info) {
            body += '<div class="info-grid">';
            body += '<div class="info-box"><div class="info-label">DFA 1</div><div class="info-value">' + json.dfa1_info.num_states + ' state, ' + json.dfa1_info.num_transitions + ' transisi</div></div>';
            body += '<div class="info-box"><div class="info-label">DFA 2</div><div class="info-value">' + json.dfa2_info.num_states + ' state, ' + json.dfa2_info.num_transitions + ' transisi</div></div>';
            body += '</div>';
        }

        // Reason
        body += '<h4>Hasil</h4><p style="font-size:0.9rem">' + json.reason + '</p>';

        // Witness string
        if (json.witness) {
            body += '<h4>String Pembeda (Witness)</h4>';
            body += '<div class="step-item" style="border-left-color:var(--danger)"><span class="step-desc" style="font-family:var(--font-mono);color:var(--danger)">"' + json.witness + '"</span>';
            body += '<div class="step-detail">String ini diterima oleh salah satu DFA tetapi ditolak oleh yang lain.</div></div>';
        }

        // Steps
        if (json.steps && json.steps.length > 0) {
            body += '<h4>Langkah Product Construction</h4>';
            json.steps.forEach(s => {
                const isOk = s.result && s.result.includes('OK');
                const isFail = s.result && (s.result.includes('TIDAK') || s.result.includes('GAGAL'));
                body += '<div class="step-item">';
                body += '<div class="step-label">Langkah ' + s.step + '</div>';
                body += '<div class="step-desc">' + s.description + '</div>';
                if (s.detail) body += '<div class="step-detail">' + s.detail + '</div>';
                if (s.transitions) {
                    s.transitions.forEach(t => { body += '<div class="transition-line">' + t + '</div>'; });
                }
                if (s.result) {
                    const cls = isFail ? 'fail' : (isOk ? 'ok' : '');
                    body += '<div class="step-result ' + cls + '">' + s.result + '</div>';
                }
                body += '</div>';
            });
        }

        // Visited pairs
        if (json.visited_pairs && json.visited_pairs.length > 0) {
            body += '<h4>Pasangan State yang Dikunjungi (' + json.visited_pairs.length + ')</h4>';
            body += '<table><thead><tr><th>DFA 1</th><th>DFA 2</th><th>Accept 1</th><th>Accept 2</th><th>Path</th></tr></thead><tbody>';
            json.visited_pairs.forEach(p => {
                body += '<tr><td>' + p.state_dfa1 + '</td><td>' + p.state_dfa2 + '</td>';
                body += '<td style="color:' + (p.accept_dfa1 ? 'var(--success)' : 'var(--text-muted)') + '">' + (p.accept_dfa1 ? 'Ya' : 'Tidak') + '</td>';
                body += '<td style="color:' + (p.accept_dfa2 ? 'var(--success)' : 'var(--text-muted)') + '">' + (p.accept_dfa2 ? 'Ya' : 'Tidak') + '</td>';
                body += '<td>' + (p.path || '\u03B5') + '</td></tr>';
            });
            body += '</tbody></table>';
        }

        showResult('result-equiv', json.equivalent, json.message, body);
    } catch (e) {
        showResult('result-equiv', false, 'Error', '<p>' + e.message + '</p>');
    }
}

// ═══ Preset Loader ═══
function loadPreset(feature, preset) {
    const presets = {
        'dfa-sim': {
            'ends-ab': {
                states: 'q0, q1, q2', alphabet: 'a, b', start: 'q0', accept: 'q2',
                transitions: 'q0,a=q1\nq0,b=q0\nq1,a=q1\nq1,b=q2\nq2,a=q1\nq2,b=q0',
                string: 'aab'
            }
        },
        'regex': { 'ab-star': { input: '(a|b)*ab' } },
        'dfa-min': {
            'redundant': {
                states: 'q0, q1, q2, q3, q4', alphabet: 'a, b', start: 'q0', accept: 'q3',
                transitions: 'q0,a=q1\nq0,b=q2\nq1,a=q1\nq1,b=q3\nq2,a=q1\nq2,b=q3\nq3,a=q1\nq3,b=q3\nq4,a=q4\nq4,b=q4'
            }
        },
        'equiv': {
            'same-language': {
                dfa1: {
                    states: 'q0, q1, q2', alphabet: 'a, b', start: 'q0', accept: 'q2',
                    transitions: 'q0,a=q1\nq0,b=q0\nq1,a=q1\nq1,b=q2\nq2,a=q1\nq2,b=q0'
                },
                dfa2: {
                    states: 's0, s1, s2, s3', alphabet: 'a, b', start: 's0', accept: 's2',
                    transitions: 's0,a=s1\ns0,b=s0\ns1,a=s1\ns1,b=s2\ns2,a=s3\ns2,b=s0\ns3,a=s1\ns3,b=s2'
                }
            },
            'diff-language': {
                dfa1: {
                    states: 'q0, q1, q2', alphabet: 'a, b', start: 'q0', accept: 'q2',
                    transitions: 'q0,a=q1\nq0,b=q0\nq1,a=q1\nq1,b=q2\nq2,a=q1\nq2,b=q0'
                },
                dfa2: {
                    states: 'p0, p1', alphabet: 'a, b', start: 'p0', accept: 'p1',
                    transitions: 'p0,a=p1\np0,b=p0\np1,a=p1\np1,b=p0'
                }
            }
        }
    };

    const p = presets[feature]?.[preset];
    if (!p) return;

    if (feature === 'dfa-sim') {
        document.getElementById('dfa-sim-states').value = p.states;
        document.getElementById('dfa-sim-alphabet').value = p.alphabet;
        document.getElementById('dfa-sim-start').value = p.start;
        document.getElementById('dfa-sim-accept').value = p.accept;
        document.getElementById('dfa-sim-transitions').value = p.transitions;
        document.getElementById('dfa-sim-string').value = p.string || '';
    } else if (feature === 'regex') {
        document.getElementById('regex-input').value = p.input;
    } else if (feature === 'dfa-min') {
        document.getElementById('dfa-min-states').value = p.states;
        document.getElementById('dfa-min-alphabet').value = p.alphabet;
        document.getElementById('dfa-min-start').value = p.start;
        document.getElementById('dfa-min-accept').value = p.accept;
        document.getElementById('dfa-min-transitions').value = p.transitions;
    } else if (feature === 'equiv') {
        ['dfa1', 'dfa2'].forEach(key => {
            const d = p[key];
            if (!d) return;
            document.getElementById('eq-' + key + '-states').value = d.states;
            document.getElementById('eq-' + key + '-alphabet').value = d.alphabet;
            document.getElementById('eq-' + key + '-start').value = d.start;
            document.getElementById('eq-' + key + '-accept').value = d.accept;
            document.getElementById('eq-' + key + '-transitions').value = d.transitions;
        });
    }
}
