# Quantium Enterprise Platform (Q-RECS) Makefile

.PHONY: setup test pipeline dashboard docker-build docker-up clean help

help:
	@echo "Quantium Q-RECS Developer CLI Commands:"
	@echo "  make setup        - Install dependencies and package in editable mode"
	@echo "  make test         - Run automated test suite with pytest/unittest"
	@echo "  make pipeline     - Run full end-to-end data pipeline via CLI"
	@echo "  make dashboard    - Launch interactive Streamlit Executive Dashboard"
	@echo "  make docker-build - Build multi-stage Docker container image"
	@echo "  make docker-up    - Serve Streamlit portal via Docker Compose"
	@echo "  make clean        - Remove bytecode and temporary build artifacts"

setup:
	pip install -r requirements.txt
	pip install -e .

test:
	python -m unittest discover tests

pipeline:
	python main.py --pipeline all

dashboard:
	streamlit run app.py

docker-build:
	docker build -t quantium-qrecs:latest .

docker-up:
	docker-compose up --build -d

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf *.egg-info build dist .pytest_cache
