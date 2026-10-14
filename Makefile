.PHONY: all install check test unstow

TARGET ?= $(HOME)
STOW ?= stow
STOW_FLAGS := --no-folding -d .stow -t "$(TARGET)"

all: install

install:
	@command -v "$(STOW)" >/dev/null
	@mkdir -p "$(TARGET)"
	@bash scripts/prepare-stow.sh
	$(STOW) $(STOW_FLAGS) --simulate -R home
	$(STOW) $(STOW_FLAGS) -D home
	@rm -rf .stow/home
	@bash scripts/prepare-stow.sh
	$(STOW) $(STOW_FLAGS) -S home

check:
	@test -d "$(TARGET)" || { \
		echo "Target directory is missing: $(TARGET) (run make first)" >&2; exit 1; }
	@bash scripts/prepare-stow.sh
	$(STOW) $(STOW_FLAGS) --simulate -R home

test:
	@bash tests/test-deploy.sh

unstow:
	@if [ -d .stow/home ] && [ -d "$(TARGET)" ]; then $(STOW) $(STOW_FLAGS) -D home; fi
