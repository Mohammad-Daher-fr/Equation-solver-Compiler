import unittest
from Equation_Solver import Parser, SolverVisitor


class TestSolver(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.solver = SolverVisitor()

    def solve(self, input_str):
        # Parse and solve a system given as a multiline string
        system = self.parser.parse(input_str)
        return self.solver.visit(system)

    def test_simple_2x2(self):
        input_data = """
        2x + 3y = 8
        x - y = 2
        """
        result = self.solve(input_data)
        # Expected solution: x = 2.8, y = 0.8
        self.assertAlmostEqual(result["x"], 2.8, places=6)
        self.assertAlmostEqual(result["y"], 0.8, places=6)

    def test_identity_3x3(self):
        input_data = """
        1x = 5
        1y = -3
        1z = 10
        """
        expected = {"x": 5.0, "y": -3.0, "z": 10.0}
        result = self.solve(input_data)
        self.assertEqual(result, expected)

    def test_negative_coeffs(self):
        input_data = """
        -x + y = 0
        2x - 4y = -2
        """
        result = self.solve(input_data)
        self.assertAlmostEqual(result["x"], 1.0, places=6)
        self.assertAlmostEqual(result["y"], 1.0, places=6)

    def test_singular(self):
        # singular system should return a dict (using pseudo-inverse)
        input_data = """
        x + y = 2
        2x + 2y = 4
        """
        result = self.solve(input_data)
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), {"x", "y"})

    def test_non_square_error(self):
        # raising ValueError for non-square systems
        input_data = """
        x + y = 2
        """
        with self.assertRaises(ValueError):
            self.solve(input_data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
