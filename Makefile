setup:
	python setup.py develop
	pip install -r requirements_test.txt

test:
	flake8 . --max-line-length=120 --exclude=.git,*/migrations/*,*/static/*,*__init__* --ignore=E731
	./manage.py test ${ARGS}
