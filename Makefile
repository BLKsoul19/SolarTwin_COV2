.PHONY: test lint fmt type-check clean

test:
	pytest tests/unit/ -v --cov=packages --cov-report=term-missing

lint:
	ruff check . && ruff format --check .

fmt:
	ruff format .

type-check:
	mypy packages/pv-twin/src/pv_twin apps

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', 'htmlcov', '.mypy_cache', '.ruff_cache']]"
