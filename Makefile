PYTHON ?= python3
PYTHONPATH := src

.PHONY: test update fixtures install lint

test:
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

update:
	@$(PYTHON) scripts/update_user_agents.py

fixtures:
	@$(PYTHON) scripts/refresh_test_fixtures.py

install:
	@$(PYTHON) -m pip install -e ".[dev]"

lint:
	@ruff check src tests scripts