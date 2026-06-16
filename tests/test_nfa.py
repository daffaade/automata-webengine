import unittest
from automata.nfa import NFA, EPSILON

class TestNFA(unittest.TestCase):
    def setUp(self):
        # NFA menerima string berakhiran 'ab' dengan epsilon transitions
        self.nfa = NFA(
            states=['q0', 'q1', 'q2', 'q3'],
            alphabet=['a', 'b'],
            transitions={
                'q0': {'a': ['q0', 'q1'], 'b': ['q0']},
                'q1': {'b': ['q2']},
                'q2': {EPSILON: ['q3']}
            },
            start_state='q0',
            accept_states=['q3']
        )

    def test_epsilon_closure(self):
        closure = self.nfa.epsilon_closure({'q2'})
        self.assertEqual(set(closure), {'q2', 'q3'})

        closure_q0 = self.nfa.epsilon_closure({'q0'})
        self.assertEqual(set(closure_q0), {'q0'})

    def test_move(self):
        moved = self.nfa.move({'q0'}, 'a')
        self.assertEqual(set(moved), {'q0', 'q1'})

        moved_b = self.nfa.move({'q1'}, 'b')
        self.assertEqual(set(moved_b), {'q2'})

    def test_simulate_accepted(self):
        self.assertTrue(self.nfa.simulate('ab'))
        self.assertTrue(self.nfa.simulate('aab'))
        self.assertTrue(self.nfa.simulate('bbab'))

    def test_simulate_rejected(self):
        self.assertFalse(self.nfa.simulate('a'))
        self.assertFalse(self.nfa.simulate('aba'))
        self.assertFalse(self.nfa.simulate(''))

if __name__ == '__main__':
    unittest.main()
