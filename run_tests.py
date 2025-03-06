import os
import unittest
import sys

def run_all_tests():
    """Run all tests in the project"""
    print("Running all tests for Pickleball App...")
    
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test modules
    test_modules = [
        'test_models',
        'test_api'
    ]
    
    # Load tests from each module
    for module in test_modules:
        try:
            # Import the module
            __import__(module)
            # Add tests from the module
            module_tests = unittest.defaultTestLoader.loadTestsFromName(module)
            test_suite.addTest(module_tests)
            print(f"Added tests from {module}")
        except ImportError as e:
            print(f"Error importing {module}: {e}")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_tests()) 