.PHONY: install clean

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

.PHONY: install clean run dashboard extract transform load reset

install: $(VENV)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) pipeline/main.py

dashboard:
	streamlit run dashboard/app.py

extract:
	$(PYTHON) pipeline/main.py --only gdelt_benin_main

transform:
	$(PYTHON) pipeline/main.py --only tone_monthly actors_country events_by_type geo_events

load:
	$(PYTHON) pipeline/main.py

reset:
	rm -rf data/processed/*
	rm -rf data/processed/parquet/*
	rm -rf data/processed/geojson/*


clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name ".ipynb_checkpoints" -exec rm -rf {} +
	rm -rf $(VENV)
