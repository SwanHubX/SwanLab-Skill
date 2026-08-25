SKILLS_DIR := skills
DIST_DIR   := dist

SKILLS := $(patsubst $(SKILLS_DIR)/%/,%,$(wildcard $(SKILLS_DIR)/*/))

.PHONY: package clean lint format

package: clean
	@mkdir -p $(DIST_DIR)
	@for skill in $(SKILLS); do \
		(cd $(SKILLS_DIR)/$$skill && zip -qr ../../$(DIST_DIR)/$$skill.zip . -x '*/__pycache__/*' '*.pyc'); \
		echo "Packed: $$skill/ -> $(DIST_DIR)/$$skill.zip"; \
	done

lint:
	uvx ruff check --fix .

format:
	uvx ruff check --select I --fix .
	uvx ruff format .
	npx oxfmt .

clean:
	rm -rf $(DIST_DIR)
