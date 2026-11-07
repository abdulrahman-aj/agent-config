.PHONY: all install check test uninstall help check-prereqs setup

TARGET ?= $(HOME)
# Picks hosts/<HOST>/, stowed on top of home/ for per-machine files.
HOST ?= $(shell uname -n)
STOW ?= stow
STOW_FLAGS := --no-folding -d . -t "$(TARGET)"
HOST_STOW = $(STOW) --no-folding -d hosts -t "$(TARGET)"
HAS_HOST = [ -n "$(HOST)" ] && [ -d "hosts/$(HOST)" ]

all: install

install: check-prereqs
	@mkdir -p "$(TARGET)"
	@bash scripts/link-shared.sh clean "$(TARGET)"
	$(STOW) $(STOW_FLAGS) -R home
	@if $(HAS_HOST); then $(HOST_STOW) -R "$(HOST)"; fi
	@bash scripts/link-shared.sh link "$(TARGET)"
	@bash scripts/link-shared.sh record "$(TARGET)"
	@python3 scripts/agent-hooks.py install "$(TARGET)"

check: check-prereqs
	@test -d "$(TARGET)" || { \
		echo "Target directory is missing: $(TARGET) (run make first)" >&2; exit 1; }
	@bash scripts/link-shared.sh clean --check "$(TARGET)"
	$(STOW) $(STOW_FLAGS) --simulate -R home
	@if $(HAS_HOST); then $(HOST_STOW) --simulate -R "$(HOST)"; fi
	@bash scripts/link-shared.sh link --check "$(TARGET)"

test: check-prereqs
	@bash tests/test-deploy.sh
	@python3 tests/test-agent-wait.py
	@python3 tests/test-fleet-run.py
	@python3 tests/test-agent-guard.py

uninstall:
	@if [ -d home ] && [ -d "$(TARGET)" ]; then $(STOW) $(STOW_FLAGS) -D home; fi
	@if [ -d "$(TARGET)" ] && $(HAS_HOST); then $(HOST_STOW) -D "$(HOST)"; fi
	@bash scripts/link-shared.sh uninstall "$(TARGET)"
	@bash scripts/link-shared.sh forget "$(TARGET)"
	@if [ -d "$(TARGET)" ]; then python3 scripts/agent-hooks.py uninstall "$(TARGET)"; fi

check-prereqs:
	@for cmd in stow cksum python3; do command -v "$$cmd" >/dev/null || { echo "Missing required command: $$cmd" >&2; exit 1; }; done

setup:
	npm install --global ccusage

help:
	@echo "install (default) - deploy or refresh the links and hooks (run after adding/removing skills, or to repair links)"
	@echo "check             - dry-run without changing installed paths; picks up newly added skills"
	@echo "test              - test deployment, scripts and hooks in temporary homes"
	@echo "uninstall         - remove managed links and hooks (run before deleting the checkout)"
	@echo "setup             - install helper tooling (ccusage)"
	@echo "TARGET=, HOST=    - deploy for another home or host folder"
