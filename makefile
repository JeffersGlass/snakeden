python = $(shell pwd)/venv/bin/python

setup:
	python3 -m venv venv
	$(python) -m pip install -r requirements.txt

serve:
	cd src && \
	$(python) -m flask --app app run

debug:
	cd src && \
	$(python) -m flask --app app run --debug