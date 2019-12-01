init:
	chmod -R +x .githooks
	git config core.hooksPath .githooks
ssh:
	ssh-keygen -t ed25519 -a 100 -N '' -C 'Key generated for CI/CD purposes only' -f sshkey
	cat sshkey | base64 -w 0 > sshkey.base64
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
requirements:
	test ! -d venv || rm -rf venv
	python3 -m venv venv
	venv/bin/python -m pip install --upgrade pip setuptools wheel
	venv/bin/python -m pip install --upgrade boto3 python-telegram-bot
	venv/bin/python -m pip freeze | grep -v "pkg-resources" > requirements.txt
lint:
	command -v flake8 || pip install --upgrade flake8
	flake8
test:
	command -v pytest || pip install --upgrade pytest pytest-cov pytest-subtests
	pytest
clean:
	find . -type f -name '*.pyc' -exec rm -rf {} \;
	find . -type f -name '*.pyo' -exec rm -rf {} \;
	find . -type f -name '*.coverage' -exec rm -rf {} \;
	find . -depth -type d -name '__pycache__' -exec rm -rf {} \;
	find . -depth -type d -name '.pytest_cache' -exec rm -rf {} \;
