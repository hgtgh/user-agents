PYTHON ?= python3
PYTHONPATH := src

.PHONY: test update fixtures

test:
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

update:
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/update_user_agents.py

fixtures:
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/refresh_test_fixtures.py
