install:
	pip install -r requirements.txt

setup: install
	pip install -r requirements-test.txt

test:
	pytest -x -s -v . --cov=now_you_rest/ --cov-report=term --cov-report=html --cov-report=xml --show-capture=no

lint: 
	flake8 --statistics

clean:
	rm -rf cover
	rm -rf dist
	rm -rf build
	rm -rf now_you_rest.egg-info
	find . -name '__pycache__' | xargs rm -Rf
	find . -name '*.pyc' | xargs rm -Rf

upload: clean
	python -m build
	twine upload dist/*