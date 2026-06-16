import unittest
from automata.dfa import DFA
from automata.minimizer import minimize_dfa, check_equivalence

class TestMinimizer(unittest.TestCase):
    def setUp(self):
        # DFA yang tidak minimal (q1 dan q2 bisa digabung)
        # Keduanya mengarah ke q3 jika input 'b' dan q1 jika 'a'
        self.dfa = DFA(
            states=['q0', 'q1', 'q2', 'q3', 'q4_dead'],
            alphabet=['a', 'b'],
            transitions={
                'q0': {'a': 'q1', 'b': 'q2'},
                'q1': {'a': 'q1', 'b': 'q3'},
                'q2': {'a': 'q1', 'b': 'q3'},
                'q3': {'a': 'q1', 'b': 'q3'},
                'q4_dead': {'a': 'q4_dead', 'b': 'q4_dead'}  # unreachable
            },
            start_state='q0',
            accept_states=['q3']
        )

    def test_minimize_dfa(self):
        min_dfa, steps = minimize_dfa(self.dfa)
        
        # q4 harus dihapus karena unreachable
        # q1 dan q2 harus disatukan, q3 tetap
        # Total state awal = 5, minimal harusnya 3 (q0, q1+q2, q3)
        self.assertEqual(len(min_dfa.states), 3)

        # Cek apakah behavior sama (ekuivalen)
        self.assertTrue(min_dfa.simulate('ab')[0])
        self.assertTrue(min_dfa.simulate('bb')[0])
        self.assertTrue(min_dfa.simulate('ababb')[0])
        
        self.assertFalse(min_dfa.simulate('a')[0])
        self.assertFalse(min_dfa.simulate('b')[0])

    def test_check_equivalence_true(self):
        min_dfa, _ = minimize_dfa(self.dfa)
        is_equivalent, reason = check_equivalence(self.dfa, min_dfa)
        self.assertTrue(is_equivalent)

    def test_check_equivalence_false(self):
        # DFA beda: menerima string yang berakhiran 'a'
        dfa2 = DFA(
            states=['q0', 'q1'],
            alphabet=['a', 'b'],
            transitions={'q0': {'a': 'q1', 'b': 'q0'}, 'q1': {'a': 'q1', 'b': 'q0'}},
            start_state='q0',
            accept_states=['q1']
        )
        is_equivalent, reason = check_equivalence(self.dfa, dfa2)
        self.assertFalse(is_equivalent)

if __name__ == '__main__':
    unittest.main()
