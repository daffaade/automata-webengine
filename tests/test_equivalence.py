import unittest
import sys
import os

# Memastikan folder root proyek masuk ke dalam sistem path agar modul automata bisa dibaca
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automata.dfa import DFA
from automata.equivalence import check_equivalence, get_equivalence_details
from automata.minimizer import minimize_dfa


class TestEquivalence(unittest.TestCase):
    """
    Suite pengujian untuk fitur Pemeriksaan Ekuivalensi Dua DFA.

    Menguji berbagai skenario:
      - DFA identik
      - DFA asli vs hasil minimasi
      - DFA dengan state berbeda tapi bahasa sama
      - DFA dengan bahasa berbeda
      - DFA dengan alphabet berbeda
      - Edge case (empty language, universal language)
    """

    def setUp(self):
        # DFA 1: menerima string yang diakhiri 'ab' (3 states)
        self.dfa_ends_ab_small = DFA(
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

        # DFA 2: menerima string yang diakhiri 'ab' (4 states, ada redundan)
        self.dfa_ends_ab_big = DFA(
            states=['s0', 's1', 's2', 's3'],
            alphabet=['a', 'b'],
            transitions={
                's0': {'a': 's1', 'b': 's0'},
                's1': {'a': 's1', 'b': 's2'},
                's2': {'a': 's3', 'b': 's0'},
                's3': {'a': 's1', 'b': 's2'}
            },
            start_state='s0',
            accept_states=['s2']
        )

        # DFA 3: menerima string yang diakhiri 'a' (2 states)
        self.dfa_ends_a = DFA(
            states=['p0', 'p1'],
            alphabet=['a', 'b'],
            transitions={
                'p0': {'a': 'p1', 'b': 'p0'},
                'p1': {'a': 'p1', 'b': 'p0'}
            },
            start_state='p0',
            accept_states=['p1']
        )

        # DFA 4: menerima semua string (universal language)
        self.dfa_universal = DFA(
            states=['u0'],
            alphabet=['a', 'b'],
            transitions={
                'u0': {'a': 'u0', 'b': 'u0'}
            },
            start_state='u0',
            accept_states=['u0']
        )

        # DFA 5: tidak menerima string apapun (empty language)
        self.dfa_empty = DFA(
            states=['e0'],
            alphabet=['a', 'b'],
            transitions={
                'e0': {'a': 'e0', 'b': 'e0'}
            },
            start_state='e0',
            accept_states=[]
        )

        # DFA 6: DFA dengan alphabet berbeda
        self.dfa_abc = DFA(
            states=['r0', 'r1'],
            alphabet=['a', 'b', 'c'],
            transitions={
                'r0': {'a': 'r1', 'b': 'r0', 'c': 'r0'},
                'r1': {'a': 'r1', 'b': 'r0', 'c': 'r0'}
            },
            start_state='r0',
            accept_states=['r1']
        )

        # DFA 7: DFA kosong kedua (empty language) dengan struktur berbeda
        self.dfa_empty_2 = DFA(
            states=['x0', 'x1'],
            alphabet=['a', 'b'],
            transitions={
                'x0': {'a': 'x1', 'b': 'x0'},
                'x1': {'a': 'x0', 'b': 'x1'}
            },
            start_state='x0',
            accept_states=[]
        )

    # ── Test Ekuivalensi Positif ─────────────────────────────────────────────

    def test_identical_dfa_are_equivalent(self):
        """Dua DFA yang identik harus ekuivalen."""
        is_eq, reason = check_equivalence(self.dfa_ends_ab_small, self.dfa_ends_ab_small)
        self.assertTrue(is_eq)
        self.assertIn('persis sama', reason)

    def test_dfa_vs_minimized_are_equivalent(self):
        """DFA asli dan hasil minimasi-nya harus ekuivalen."""
        # DFA dengan unreachable dan redundant states
        dfa_big = DFA(
            states=['q0', 'q1', 'q2', 'q3', 'q4'],
            alphabet=['a', 'b'],
            transitions={
                'q0': {'a': 'q1', 'b': 'q2'},
                'q1': {'a': 'q1', 'b': 'q3'},
                'q2': {'a': 'q1', 'b': 'q3'},
                'q3': {'a': 'q1', 'b': 'q3'},
                'q4': {'a': 'q4', 'b': 'q4'}  # unreachable
            },
            start_state='q0',
            accept_states=['q3']
        )
        min_dfa, _ = minimize_dfa(dfa_big)
        is_eq, reason = check_equivalence(dfa_big, min_dfa)
        self.assertTrue(is_eq)

    def test_different_states_same_language(self):
        """DFA dengan nama state berbeda tapi bahasa sama harus ekuivalen."""
        # dfa_ends_ab_small dan dfa_ends_ab_big keduanya menerima string berakhiran 'ab'
        # Tapi dfa_ends_ab_big punya state s3 yang redundan (perilaku sama dengan s1)
        is_eq, reason = check_equivalence(self.dfa_ends_ab_small, self.dfa_ends_ab_big)
        self.assertTrue(is_eq)

    def test_both_empty_language_equivalent(self):
        """Dua DFA dengan empty language harus ekuivalen."""
        is_eq, reason = check_equivalence(self.dfa_empty, self.dfa_empty_2)
        self.assertTrue(is_eq)

    # ── Test Ekuivalensi Negatif ─────────────────────────────────────────────

    def test_different_language_not_equivalent(self):
        """DFA dengan bahasa berbeda harus TIDAK ekuivalen."""
        # ends_ab vs ends_a
        is_eq, reason = check_equivalence(self.dfa_ends_ab_small, self.dfa_ends_a)
        self.assertFalse(is_eq)
        self.assertIn('membedakan', reason)

    def test_different_alphabet_not_equivalent(self):
        """DFA dengan alphabet berbeda harus TIDAK ekuivalen."""
        is_eq, reason = check_equivalence(self.dfa_ends_a, self.dfa_abc)
        self.assertFalse(is_eq)
        self.assertIn('Alphabet berbeda', reason)

    def test_universal_vs_empty_not_equivalent(self):
        """Universal language vs empty language harus TIDAK ekuivalen."""
        is_eq, reason = check_equivalence(self.dfa_universal, self.dfa_empty)
        self.assertFalse(is_eq)

    def test_universal_vs_selective_not_equivalent(self):
        """Universal language vs selective language harus TIDAK ekuivalen."""
        is_eq, reason = check_equivalence(self.dfa_universal, self.dfa_ends_ab_small)
        self.assertFalse(is_eq)

    # ── Test Witness String ──────────────────────────────────────────────────

    def test_witness_string_is_valid(self):
        """Witness string harus benar-benar membedakan kedua DFA."""
        is_eq, reason = check_equivalence(self.dfa_ends_ab_small, self.dfa_ends_a)
        self.assertFalse(is_eq)

        # Ekstrak witness dari reason
        # Format: 'Ditemukan string yang membedakan: "witness"'
        import re
        match = re.search(r'"([^"]*)"', reason)
        self.assertIsNotNone(match, f"Witness tidak ditemukan dalam reason: {reason}")
        witness = match.group(1)

        if witness == 'ε':
            witness = ''

        # Witness harus accepted oleh satu DFA tapi rejected oleh yang lain
        acc1, _ = self.dfa_ends_ab_small.simulate(witness)
        acc2, _ = self.dfa_ends_a.simulate(witness)
        self.assertNotEqual(acc1, acc2,
            f'Witness "{witness}" tidak benar-benar membedakan: '
            f'DFA1={acc1}, DFA2={acc2}')

    # ── Test Detail (get_equivalence_details) ────────────────────────────────

    def test_details_equivalent(self):
        """Detail ekuivalensi harus lengkap untuk kasus ekuivalen."""
        details = get_equivalence_details(self.dfa_ends_ab_small, self.dfa_ends_ab_small)
        self.assertTrue(details['is_equivalent'])
        self.assertIsNone(details['witness'])
        self.assertGreater(len(details['steps']), 0)
        self.assertGreater(len(details['visited_pairs']), 0)
        self.assertIn('num_states', details['dfa1_info'])
        self.assertIn('num_states', details['dfa2_info'])

    def test_details_not_equivalent(self):
        """Detail ekuivalensi harus lengkap untuk kasus tidak ekuivalen."""
        details = get_equivalence_details(self.dfa_ends_ab_small, self.dfa_ends_a)
        self.assertFalse(details['is_equivalent'])
        self.assertIsNotNone(details['witness'])
        self.assertGreater(len(details['steps']), 0)

    def test_details_alphabet_mismatch(self):
        """Detail ekuivalensi untuk alphabet berbeda harus menunjukkan alasan."""
        details = get_equivalence_details(self.dfa_ends_a, self.dfa_abc)
        self.assertFalse(details['is_equivalent'])
        self.assertIn('Alphabet berbeda', details['reason'])
        # Step pertama harus gagal di pemeriksaan alphabet
        self.assertEqual(details['steps'][0]['step'], 0)
        self.assertIn('GAGAL', details['steps'][0]['result'])

    def test_details_steps_have_transitions(self):
        """Langkah BFS harus mencatat transisi yang dieksplorasi."""
        details = get_equivalence_details(self.dfa_ends_ab_small, self.dfa_ends_ab_big)
        # Cari step yang punya transitions (bukan step 0 dan bukan kesimpulan)
        steps_with_transitions = [
            s for s in details['steps']
            if 'transitions' in s
        ]
        self.assertGreater(len(steps_with_transitions), 0)

    # ── Test Backward Compatibility ──────────────────────────────────────────

    def test_import_from_minimizer_still_works(self):
        """Import check_equivalence dari minimizer harus tetap berfungsi."""
        from automata.minimizer import check_equivalence as ce_minimizer
        is_eq, reason = ce_minimizer(self.dfa_ends_ab_small, self.dfa_ends_ab_small)
        self.assertTrue(is_eq)


# ── Mode Interaktif CLI ──────────────────────────────────────────────────────

def interactive_main():
    """
    Mode interaktif untuk pemeriksaan ekuivalensi dua DFA melalui terminal.
    Mengikuti pola yang digunakan oleh test_dfa.py dan test_regex_to_nfa.py.
    """
    print("=" * 50)
    print("  PROGRAM PEMERIKSAAN EKUIVALENSI DUA DFA (CLI)")
    print("=" * 50)
    print("Masukkan definisi kedua DFA untuk diperiksa.\n")

    dfas = []
    for i in range(1, 3):
        print(f"\n{'─' * 50}")
        print(f"  DFA {i}")
        print(f"{'─' * 50}")

        states_input = input(f"  Masukkan states DFA {i} (pisahkan koma, cth: q0,q1,q2): ")
        states = [s.strip() for s in states_input.split(',')] if states_input.strip() else []

        alphabet_input = input(f"  Masukkan alphabet DFA {i} (pisahkan koma, cth: a,b): ")
        alphabet = [a.strip() for a in alphabet_input.split(',')] if alphabet_input.strip() else []

        start_state = input(f"  Masukkan start state DFA {i} (cth: q0): ").strip()

        accept_input = input(f"  Masukkan accept states DFA {i} (pisahkan koma, cth: q2): ")
        accept_states = [s.strip() for s in accept_input.split(',')] if accept_input.strip() else []

        print(f"\n  Masukkan transisi DFA {i}:")
        print("  Format: state,simbol=next_state (cth: q0,a=q1)")
        print("  Ketik 'selesai' jika sudah.\n")

        transitions = {}
        while True:
            trans_input = input("    Transisi: ").strip()
            if trans_input.lower() == 'selesai' or trans_input == '':
                break
            try:
                left, right = trans_input.split('=')
                src, symbol = left.split(',')
                transitions[f"{src.strip()},{symbol.strip()}"] = right.strip()
            except ValueError:
                print("    [!] Format salah. Gunakan: state,simbol=next_state")

        try:
            dfa = DFA(
                states=states,
                alphabet=alphabet,
                transitions=transitions,
                start_state=start_state,
                accept_states=accept_states
            )
            validation = dfa.validate()
            if not validation['valid']:
                print(f"\n  [!] DFA {i} tidak valid:")
                for err in validation['errors']:
                    print(f"    - {err}")
                return
            print(f"  [v] DFA {i} valid!")
            dfas.append(dfa)
        except Exception as e:
            print(f"\n  [!] Gagal membuat DFA {i}: {e}")
            return

    # Jalankan pemeriksaan ekuivalensi
    print(f"\n{'=' * 50}")
    print("         HASIL PEMERIKSAAN EKUIVALENSI")
    print(f"{'=' * 50}\n")

    print("Memeriksa ekuivalensi kedua DFA...\n")

    details = get_equivalence_details(dfas[0], dfas[1])

    # Tampilkan langkah-langkah
    print("--- Langkah-langkah Product Construction ---\n")
    for step in details['steps']:
        print(f"  Langkah {step['step']}: {step['description']}")
        print(f"    Detail: {step['detail']}")
        if 'transitions' in step:
            for t in step['transitions']:
                print(f"      {t}")
        print(f"    Hasil: {step['result']}")
        print()

    # Tampilkan kesimpulan
    print(f"{'─' * 50}")
    if details['is_equivalent']:
        print("  >> KESIMPULAN: Kedua DFA EKUIVALEN")
        print(f"  >> {details['reason']}")
    else:
        print("  >> KESIMPULAN: Kedua DFA TIDAK EKUIVALEN")
        print(f"  >> {details['reason']}")
        if details['witness']:
            print(f"  >> String pembeda (witness): \"{details['witness']}\"")
    print(f"{'─' * 50}")

    # Info ringkasan
    info1 = details['dfa1_info']
    info2 = details['dfa2_info']
    print(f"\n  DFA 1: {info1['num_states']} state(s), "
          f"{info1['num_transitions']} transisi")
    print(f"  DFA 2: {info2['num_states']} state(s), "
          f"{info2['num_transitions']} transisi")
    print(f"  Pasangan state yang diperiksa: {len(details['visited_pairs'])}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--unittest':
        sys.argv.pop(1)
        unittest.main()
    else:
        interactive_main()
