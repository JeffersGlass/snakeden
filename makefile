python = ./venv/bin/python

setup:
	python3 -m venv venv
	$(python) -m pip install -r requirements.txt

serve:
	$(python) -m flask --app src/app run

debug:
	$(python) -m flask --app src/app run --debug