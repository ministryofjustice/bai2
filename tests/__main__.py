import pathlib
import unittest

if __name__ == '__main__':
    tests_path = pathlib.Path(__file__).parent
    root_path = tests_path.parent
    test_suite = unittest.defaultTestLoader.discover(start_dir=str(tests_path), top_level_dir=str(root_path))
    test_runner = unittest.runner.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)
