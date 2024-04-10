python = ./venv/bin/python

setup:
	python3 -m venv venv
	$(python) -m pip install -r requirements.txt

activate:
	source ./venv/bin/activate

serve:
	$(python) -m flask run

debug:
	$(python) -m flask run --debug