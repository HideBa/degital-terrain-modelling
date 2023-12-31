PACKAGE_DIR := py

.PHONY: install
install:
	poetry install

.PHONY: update
update:
	poetry update

.PHONY: lint
lint:
	poetry run flake8 $(PACKAGE_DIR)


.PHONY: format
format:
	poetry run black $(PACKAGE_DIR)/**/*.py

.PHONY: sort
sort:
	poetry run isort $(PACKAGE_DIR)/**/*.py

.PHONY: test
test:
	poetry run pytest $(PACKAGE_DIR)


.PHONY: step3
step3:
	python $(PACKAGE_DIR)/step3.py

.PHONY: step4
step4:
	python $(PACKAGE_DIR)/step4.py

.PHONY: step5
step5:
	python $(PACKAGE_DIR)/step5.py
