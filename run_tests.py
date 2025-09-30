#!/usr/bin/env python
"""
Simple script to run tests locally with mocked database
Usage: python run_tests.py
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    # Set test settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_info_api.test_settings')
    
    # Setup Django
    django.setup()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    print("Running tests with in-memory SQLite database...")
    print("No external database required!")
    print("-" * 50)
    
    # Run tests
    failures = test_runner.run_tests(["api.tests"])
    
    if failures:
        print(f"\n{failures} test(s) failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        print("Ready to push to GitHub Actions!")


if __name__ == '__main__':
    run_tests()
