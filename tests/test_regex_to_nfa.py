import unittest
import sys
import os

# Memastikan folder root proyek masuk ke dalam sistem path agar modul automata bisa dibaca
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automata.regex_to_nfa import regex_to_nfa

class TestRegexToNFA(unittest.TestCase):
    def test_basic_symbol(self):
        nfa = regex_to_nfa("a")
        self.assertTrue(nfa.simulate("a"))
        with self.assertRaises(ValueError):
            nfa.simulate("b")

    def test_concatenation(self):
        nfa = regex_to_nfa("ab")
        self.assertTrue(nfa.simulate("ab"))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("aba"))

    def test_union(self):
        nfa = regex_to_nfa("a|b")
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("ab"))

    def test_kleene_star(self):
        nfa = regex_to_nfa("a*")
        self.assertTrue(nfa.simulate(""))
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("aa"))
        self.assertTrue(nfa.simulate("aaa"))
        with self.assertRaises(ValueError):
            nfa.simulate("b")

    def test_complex_expression(self):
        # Menerima string berakhiran 'ab'
        nfa = regex_to_nfa("(a|b)*ab")
        self.assertTrue(nfa.simulate("ab"))
        self.assertTrue(nfa.simulate("aab"))
        self.assertTrue(nfa.simulate("bbab"))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("aba"))

    def test_plus_as_union(self):
        # Dalam konvensi TBA, '+' berarti union (alternasi), sama seperti '|'
        nfa = regex_to_nfa("a+b")
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("ab"))
        self.assertFalse(nfa.simulate(""))

    def test_tba_regex_bb(self):
        # Regex TBA: (a+b)*bb(a+b)* — menerima string yang mengandung 'bb'
        nfa = regex_to_nfa("(a+b)*bb(a+b)*")
        self.assertTrue(nfa.simulate("bb"))
        self.assertTrue(nfa.simulate("abb"))
        self.assertTrue(nfa.simulate("bba"))
        self.assertTrue(nfa.simulate("babba"))
        self.assertTrue(nfa.simulate("aabb"))
        self.assertFalse(nfa.simulate("a"))
        self.assertFalse(nfa.simulate("b"))
        self.assertFalse(nfa.simulate("aba"))

    def test_optional(self):
        # Operator '?' (optional) — nol atau satu kali
        nfa = regex_to_nfa("ab?")
        self.assertTrue(nfa.simulate("a"))
        self.assertTrue(nfa.simulate("ab"))
        self.assertFalse(nfa.simulate(""))
        self.assertFalse(nfa.simulate("abb"))

    def test_simulate_verbose(self):
        nfa = regex_to_nfa("ab")
        res = nfa.simulate_verbose("ab")
        self.assertTrue(res["accepted"])
        self.assertEqual(res["result"], "Accepted")
        self.assertEqual(len(res["history"]), 2)
        # Langkah pertama membaca 'a'
        self.assertEqual(res["history"][0]["symbol"], "a")
        # Langkah kedua membaca 'b'
        self.assertEqual(res["history"][1]["symbol"], "b")

def interactive_main():
    print("========================================")
    print("  PROGRAM CONVERT REGEX TO NFA (CLI)    ")
    print("========================================")
    print("Ketik 'keluar' untuk menghentikan program.\n")

    while True:
        regex_input = input("Masukkan Regular Expression (cth: (a|b)*ab): ").strip()
        if regex_input.lower() == 'keluar':
            print("Terima kasih telah menggunakan program Regex ke NFA!")
            break
        if not regex_input:
            print("[!] Regex tidak boleh kosong.\n")
            continue

        try:
            print("\nMenerjemahkan regex ke NFA...")
            nfa = regex_to_nfa(regex_input)
            print("[v] Sukses mengonversi Regex ke NFA!")
            
            # Tampilkan informasi NFA
            print("\n--- Detail NFA yang Terbentuk ---")
            print(f"States        : {', '.join(nfa.states)}")
            print(f"Alphabet      : {', '.join(nfa.alphabet)}")
            print(f"Start State   : {nfa.start_state}")
            print(f"Accept States : {', '.join(nfa.accept_states)}")
            print("Transitions   :")
            
            # Format transisi agar mudah dibaca
            for state in sorted(nfa.transitions.keys()):
                symbols = nfa.transitions[state]
                for symbol, next_states in sorted(symbols.items()):
                    next_str = ", ".join(sorted(next_states))
                    symbol_display = symbol if symbol != 'ε' else 'epsilon (ε)'
                    print(f"   δ({state}, {symbol_display}) = {{{next_str}}}")
            print("-" * 33)

        except Exception as e:
            print(f"[!] Gagal mengonversi Regex ke NFA: {e}\n")
            continue

        # Loop testing string untuk NFA ini
        print("\n========================================")
        print("    TESTING STRING UNTUK NFA TERSEBUT   ")
        print("========================================")
        print("Ketik 'kembali' untuk memasukkan Regex baru.\n")

        while True:
            test_string = input("Masukkan string untuk ditest: ").strip()
            if test_string.lower() == 'kembali':
                print()
                break
            if test_string.lower() == 'keluar':
                print("Terima kasih telah menggunakan program Regex ke NFA!")
                return

            print(f"\n>> Menjalankan simulasi NFA untuk: '{test_string}'")
            try:
                result = nfa.simulate_verbose(test_string)
                
                print(">> Hasil          : ", result["result"])
                print(">> Final States   : ", "{" + ", ".join(result["final_states"]) + "}")
                print(">> State History  :")
                
                for step in result["history"]:
                    curr_set = "{" + ", ".join(step["current_states"]) + "}"
                    
                    if "error" in step:
                        print(f"   {curr_set} --({step['symbol']})--> [DITOLAK: {step['error']}]")
                    else:
                        next_set = "{" + ", ".join(step["next_states"]) + "}"
                        print(f"   {curr_set} --({step['symbol']})--> {next_set}")
                print("-" * 40)
            except Exception as e:
                print(f"   [!] Error saat simulasi: {e}")
                print("-" * 40)

if __name__ == '__main__':
    # Jika dijalankan dengan argumen --unittest, jalankan suite pengujian unittest
    if len(sys.argv) > 1 and sys.argv[1] == '--unittest':
        sys.argv.pop(1)
        unittest.main()
    else:
        # Secara default, jalankan mode interaktif CLI
        interactive_main()
