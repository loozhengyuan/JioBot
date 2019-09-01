install:
	pip install --upgrade pip
	pip install -r requirements.txt
lint:
	pip install --upgrade flake8
	flake8