# Makes the repo root importable as `teach.*` from tests, without needing a
# build backend / editable install. pytest inserts this file's directory
# onto sys.path (prepend import mode) when it collects conftest.py.
