install:
	pip install -r requirements.txt

setup: install
	pip install -r requirements-test.txt

run-local:
	python app.py

test:
	pytest -x -s -v . --cov=apify/ --cov-report=term --cov-report=html --cov-report=xml

lint: 
	flake8 --statistics