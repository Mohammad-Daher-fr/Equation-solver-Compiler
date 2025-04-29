@echo off
REM Run all Python unittests in the tests/ directory
python -m unittest discover -s tests -p "test_*.py" -v
