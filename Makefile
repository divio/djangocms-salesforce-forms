setup:
	pip install -r tests/requirements.txt

test:
	flake8 djangocms_salesforce_forms --max-line-length=120 --ignore=E731,W391,F401 --exclude=.*,*/migrations/*,*/static/*,*__init__*
	coverage erase
	coverage run setup.py test
	coverage report
