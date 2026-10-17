.PHONY: all install check test unstow help check-prereqs _install _check _unstow

TARGET ?= $(HOME)
STOW ?= stow
STOW_FLAGS := --no-folding -d .stow -t "$(TARGET)"

all: install

install: check-prereqs
	@mkdir -p .stow; exec 9>.stow/lock; flock -n 9 || { echo "install: another make is running" >&2; exit 1; }; $(MAKE) _install TARGET="$(TARGET)"

_install:
	@mkdir -p "$(TARGET)"
	@bash scripts/prepare-stow.sh
	@bash scripts/repair-stale.sh "$(TARGET)"
	$(STOW) $(STOW_FLAGS) --simulate -R home
	$(STOW) $(STOW_FLAGS) -D home
	@rm -rf .stow/home
	@bash scripts/prepare-stow.sh
	$(STOW) $(STOW_FLAGS) -S home
	@bash scripts/repair-stale.sh record "$(TARGET)"

check: check-prereqs
	@test -d "$(TARGET)" || { \
		echo "Target directory is missing: $(TARGET) (run make first)" >&2; exit 1; }
	@mkdir -p .stow; exec 9>.stow/lock; flock -n 9 || { echo "check: another make is running" >&2; exit 1; }; $(MAKE) _check TARGET="$(TARGET)"

_check:
	@bash scripts/prepare-stow.sh
	@bash scripts/repair-stale.sh --check "$(TARGET)"
	$(STOW) $(STOW_FLAGS) --simulate -R home

test: check-prereqs
	@bash tests/test-deploy.sh

unstow:
	@mkdir -p .stow; exec 9>.stow/lock; flock -n 9 || { echo "unstow: another make is running" >&2; exit 1; }; $(MAKE) _unstow TARGET="$(TARGET)"

_unstow:
	@if [ -d .stow/home ] && [ -d "$(TARGET)" ]; then $(STOW) $(STOW_FLAGS) -D home; fi
	@bash scripts/repair-stale.sh forget "$(TARGET)"

check-prereqs:
	@for cmd in bash stow find ln mkdir realpath flock cksum; do command -v "$$cmd" >/dev/null || { echo "Missing required command: $$cmd" >&2; exit 1; }; done

help:
	@echo "install (default) - deploy or refresh the shared links (run after adding/removing skills, or to repair links)"
	@echo "check             - dry-run without changing installed paths; picks up newly added skills"
	@echo "test              - test deployment and preservation in a temporary home"
	@echo "unstow            - remove managed links (run before deleting the checkout)"
	@echo "TARGET=/path      - deploy for another home (with install, check)"
	@echo "conflicts are never auto-resolved; move an offending path aside and rerun"
