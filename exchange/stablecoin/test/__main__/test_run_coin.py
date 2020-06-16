import unittest
from test.util.captured_output import captured_output

from run_coin import main

class TestMain(unittest.TestCase):

    """Test the main funcion"""

    def test_main(self):

        with captured_output() as (out, err):
            main()
            output = out.getvalue().strip()

        with captured_output() as (out, err):
            print("ing")
            print("database")
            print("trustchain")
            # print("rest")
            expected = out.getvalue().strip()

        self.assertEqual(output, expected)
