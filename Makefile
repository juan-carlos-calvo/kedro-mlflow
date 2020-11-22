clean:
	rm -rf build dist pip-wheel-metadata .pytest_cache
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	find . -regex ".*\.egg-info" -exec rm -rf {} +

install:
	pip install .

install-pip-setuptools:
	python -m pip install -U "pip>=18.0, <21.0" "setuptools>=38.0, <47.0" wheel

lint:
	pre-commit run -a --hook-stage manual

test:
	pytest tests

secret-scan:
	trufflehog --max_depth 1 .

package: clean install
	python setup.py clean --all
	python setup.py sdist bdist_wheel

legal:
	python tools/license_and_headers.py
