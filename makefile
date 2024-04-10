python = $(shell pwd)/venv/bin/python

setup:
	python3 -m venv venv
	$(python) -m pip install -r requirements.txt

serve:
	cd flask-src && \
	$(python) -m flask --app app run

debug:
	cd flask-src && \
	$(python) -m flask --app app run --debug