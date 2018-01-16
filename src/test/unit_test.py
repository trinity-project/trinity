import unittest
import os

if __name__ == "__main__":
    path = os.path.dirname(__file__)
    test_suite = unittest.TestLoader().discover(path, "test*.py")
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
