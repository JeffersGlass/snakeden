# Snakeden - Distributed pypeformance runs

![The Snakeden web interface](./screenshot.png)

## Information

This is a personal experimental project, and should not be relied upon at the moment.

## Usage

### Installation

1. Clone this repo
2. Run `make setup`
3. (Optionally) activate the virtual environment with `source ./venv/bin/activate`

### Running a Dev Server
Run `make debug` to run the local dev server in the browser. Go to the root url (`/`) to view the interactive interface.

## Running Raw Dask Commands

### Scheduler

```sh
cd flask-src && ../venv/bin/python -m dask scheduler
```

### Worker
```
cd flask-src && ../venv/bin/python -m dask worker --resources "CPU=1"
```
