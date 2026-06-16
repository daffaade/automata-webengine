import unittest
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

if __name__ == '__main__':
    unittest.main()
