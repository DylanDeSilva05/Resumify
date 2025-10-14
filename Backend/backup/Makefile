# Resumify Backend Makefile

.PHONY: help install dev test security clean

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Run development server"
	@echo "  test       - Run tests"
	@echo "  security   - Run security checks"
	@echo "  security-install - Install security tools"
	@echo "  clean      - Clean cache and temp files"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

security-install:
	pip install bandit safety

security:
	@echo "Running comprehensive security checks..."
	python scripts/security_check.py

security-quick:
	@echo "Running quick security scan..."
	bandit -r app/ -ll
	safety check

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +