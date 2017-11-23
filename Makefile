setup:
	pip install -r tests/requirements.txt

test:
	flake8 . --max-line-length=120 --exclude=.git,.eggs,*/migrations/*,*/static/*,*__init__* --ignore=E731
	coverage run ./setup.py test
	coverage report
