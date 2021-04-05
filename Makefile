setup:
	pip install -Ue .\[tests\]

test:
	pytest -x -s -v . --cov=py_easy_rest/ --cov-report=term --cov-report=html --cov-report=xml --show-capture=no

lint: 
	flake8 --statistics

clean:
	rm -rf cover
	rm -rf dist
	rm -rf build
	rm -rf py_easy_rest.egg-info
	find . -name '__pycache__' | xargs rm -Rf
	find . -name '*.pyc' | xargs rm -Rf

build:
	python -m build

upload:
	twine upload dist/*