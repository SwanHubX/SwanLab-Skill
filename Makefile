SKILLS_DIR := skills
DIST_DIR   := dist

SKILLS := $(patsubst $(SKILLS_DIR)/%/,%,$(wildcard $(SKILLS_DIR)/*/))

.PHONY: package clean lint format bump-version

VERSION ?=

ifeq ($(shell uname),Darwin)
SED_I := sed -i ''
else
SED_I := sed -i
endif

bump-version:
ifndef VERSION
	@echo "Usage: make bump-version VERSION=x.y.z"; exit 1
endif
	@current="$$(sed -n 's/^  version: "\([^"]*\)"[[:space:]]*$$/\1/p' skills/swanlab-skill/SKILL.md)"; \
	if [[ -z "$$current" || "$$current" == *$$'\n'* ]]; then \
		echo "error: expected exactly one metadata.version in skills/swanlab-skill/SKILL.md"; exit 1; \
	fi; \
	if ! [[ "$(VERSION)" =~ ^[0-9][0-9A-Za-z._-]*$$ ]]; then \
		echo "error: unsupported version $(VERSION)"; exit 1; \
	fi; \
	if [[ "$(VERSION)" == "$$current" ]]; then \
		echo "Version already at $(VERSION); nothing to do."; exit 0; \
	fi; \
	$(SED_I) 's/^  version: "\([^"]*\)"[[:space:]]*$$/  version: "$(VERSION)"/' skills/swanlab-skill/SKILL.md; \
	$(SED_I) -E 's|badge/Skill-v[0-9A-Za-z._-]+-([0-9a-f]{6})|badge/Skill-v$(VERSION)-\1|' README.md README_EN.md; \
	grep -Fq 'version: "$(VERSION)"' skills/swanlab-skill/SKILL.md || { echo "error: SKILL.md update failed"; exit 1; }; \
	grep -Fq "Skill-v$(VERSION)-" README.md || { echo "error: README.md badge update failed"; exit 1; }; \
	grep -Fq "Skill-v$(VERSION)-" README_EN.md || { echo "error: README_EN.md badge update failed"; exit 1; }; \
	echo "Bumped version: $$current -> $(VERSION) (SKILL.md, README.md, README_EN.md)"

package: clean
	@mkdir -p $(DIST_DIR)
	@for skill in $(SKILLS); do \
		(cd $(SKILLS_DIR) && zip -qr ../$(DIST_DIR)/$$skill.zip $$skill -x '*/__pycache__/*' '*.pyc'); \
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
