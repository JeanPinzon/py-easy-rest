install:
	pip install -r requirements.txt

setup: install
	pip install -r requirements-test.txt

run-local:
	python app.py

test:
	pytest -x -s -v . --cov=now_you_rest/ --cov-report=term --cov-report=html --cov-report=xml

lint: 
	flake8 --statistics

run-mongo:
	docker run -p 27017:27017 mongo

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