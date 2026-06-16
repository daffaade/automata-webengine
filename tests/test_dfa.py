import unittest
import sys
import os

# Memastikan folder root proyek masuk ke dalam sistem path agar modul automata bisa dibaca
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automata.dfa import DFA

class TestDFA(unittest.TestCase):
    def setUp(self):
        # DFA menerima string yang diakhiri dengan 'ab'
        self.dfa = DFA(
            states=['q0', 'q1', 'q2'],
            alphabet=['a', 'b'],
            transitions={
                'q0': {'a': 'q1', 'b': 'q0'},
                'q1': {'a': 'q1', 'b': 'q2'},
                'q2': {'a': 'q1', 'b': 'q0'}
            },
            start_state='q0',
            accept_states=['q2']
        )

    def test_validate_success(self):
        validation = self.dfa.validate()
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)

    def test_validate_failure_invalid_start_state(self):
        self.dfa.start_state = 'q99'
        validation = self.dfa.validate()
        self.assertFalse(validation['valid'])
        self.assertTrue(any('Start state' in err for err in validation['errors']))

    def test_simulate_accepted(self):
        accepted, path = self.dfa.simulate('ab')
        self.assertTrue(accepted)
        self.assertEqual(path, ['q0', 'q1', 'q2'])

        accepted, path = self.dfa.simulate('aab')
        self.assertTrue(accepted)
        self.assertEqual(path, ['q0', 'q1', 'q1', 'q2'])

    def test_simulate_rejected(self):
        accepted, path = self.dfa.simulate('a')
        self.assertFalse(accepted)
        self.assertEqual(path, ['q0', 'q1'])

        accepted, path = self.dfa.simulate('aba')
        self.assertFalse(accepted)
        self.assertEqual(path, ['q0', 'q1', 'q2', 'q1'])

    def test_simulate_verbose(self):
        result = self.dfa.simulate_verbose('aab')
        self.assertTrue(result['accepted'])
        self.assertEqual(result['result'], 'Accepted')
        self.assertEqual(result['final_state'], 'q2')
        self.assertEqual(len(result['history']), 3)
        self.assertEqual(result['history'][0], {'current_state': 'q0', 'symbol': 'a', 'next_state': 'q1'})
        self.assertEqual(result['history'][1], {'current_state': 'q1', 'symbol': 'a', 'next_state': 'q1'})
        self.assertEqual(result['history'][2], {'current_state': 'q1', 'symbol': 'b', 'next_state': 'q2'})

def interactive_main():
    import sys
    print("========================================")
    print("   PROGRAM SIMULATOR DFA (INTERAKTIF)   ")
    print("========================================")
    print("Masukkan definisi DFA sesuai ketentuan:\n")

    # 1. Input States
    states_input = input("1. Masukkan himpunan states (pisahkan dengan koma, cth: q0,q1,q2): ")
    states = [s.strip() for s in states_input.split(',')] if states_input.strip() else []

    # 2. Input Alphabet
    alphabet_input = input("2. Masukkan alphabet (pisahkan dengan koma, cth: a,b): ")
    alphabet = [a.strip() for a in alphabet_input.split(',')] if alphabet_input.strip() else []

    # 3. Input Start State
    start_state = input("3. Masukkan Start State (cth: q0): ").strip()

    # 4. Input Accept States
    accept_input = input("4. Masukkan Accept States / Final States (pisahkan dengan koma, cth: q2): ")
    accept_states = [s.strip() for s in accept_input.split(',')] if accept_input.strip() else []

    # 5. Input Transitions
    print("\n5. Masukkan Fungsi Transisi:")
    print("Format: state,simbol=next_state (cth: q0,a=q1)")
    print("Ketik 'selesai' jika sudah selesai memasukkan transisi.")
    
    transitions = {}
    while True:
        trans_input = input("   Transisi: ").strip()
        if trans_input.lower() == 'selesai' or trans_input == '':
            break
        
        try:
            left, right = trans_input.split('=')
            src, symbol = left.split(',')
            src = src.strip()
            symbol = symbol.strip()
            dest = right.strip()
            transitions[f"{src},{symbol}"] = dest
        except ValueError:
            print("   [!] Format salah. Gunakan format: state,simbol=next_state (cth: q0,a=q1)")

    # Buat instance DFA
    try:
        dfa = DFA(
            states=states,
            alphabet=alphabet,
            transitions=transitions,
            start_state=start_state,
            accept_states=accept_states
        )
    except Exception as e:
        print("\n[!] Gagal membuat DFA:", e)
        return

    # Validasi DFA
    print("\nMemvalidasi DFA...")
    validation = dfa.validate()
    if not validation["valid"]:
        print("[!] DFA Tidak Valid. Ditemukan kesalahan:")
        for err in validation["errors"]:
            print("  -", err)
        return
    else:
        print("[v] DFA Valid dan siap digunakan!")

    # 6. Loop Testing String
    print("\n========================================")
    print("             TESTING STRING             ")
    print("========================================")
    print("Ketik 'keluar' untuk mengakhiri program.\n")

    while True:
        test_string = input("Masukkan string untuk ditest: ").strip()
        if test_string.lower() == 'keluar':
            print("Terima kasih telah menggunakan simulator DFA!")
            break
            
        print(f"\n>> Menjalankan simulasi untuk: '{test_string}'")
        try:
            result = dfa.simulate_verbose(test_string)
            
            print(">> Hasil: ", result["result"])
            print(">> Final State: ", result["final_state"])
            print(">> State History:")
            for step in result["history"]:
                if step["next_state"] is not None:
                    print(f"   {step['current_state']} --({step['symbol']})--> {step['next_state']}")
                else:
                    print(f"   {step['current_state']} --({step['symbol']})--> [DITOLAK: {step.get('error', 'Transisi tidak ada')}]")
            print("-" * 40)
        except Exception as e:
            print(f"   [!] Error saat simulasi: {e}")
            print("-" * 40)

if __name__ == '__main__':
    import sys
    # Jika dijalankan dengan argumen --unittest, maka jalankan unit test
    if len(sys.argv) > 1 and sys.argv[1] == '--unittest':
        sys.argv.pop(1)
        unittest.main()
    else:
        # Secara default, jalankan mode interaktif
        interactive_main()
