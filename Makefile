SKILLS_DIR := skills
DIST_DIR   := dist

SKILLS := $(patsubst $(SKILLS_DIR)/%/,%,$(wildcard $(SKILLS_DIR)/*/))

.PHONY: pack clean

pack:
	@mkdir -p $(DIST_DIR)
	@for skill in $(SKILLS); do \
		(cd $(SKILLS_DIR) && zip -r ../$(DIST_DIR)/$$skill.zip $$skill/); \
		echo "Packed: $$skill/ -> $(DIST_DIR)/$$skill.zip"; \
	done

clean:
	rm -rf $(DIST_DIR)
