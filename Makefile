.PHONY: extract clean dashboard install

install:
	pip install -r requirements.txt

extract:
	python pipeline/extract.py

transform:
	python pipeline/transform.py

load:
	python pipeline/load.py

all: extract transform load

dashboard:
	streamlit run dashboard/app.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name ".ipynb_checkpoints" -exec rm -rf {} +