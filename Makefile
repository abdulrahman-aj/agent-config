.PHONY: all deploy install check test uninstall help check-prereqs setup

TARGET ?= $(HOME)
# The pinned checkout agents load from; `make deploy` keeps it at origin/main.
DEPLOY_DIR ?= $(HOME)/.local/share/agent-config
# Picks hosts/<HOST>/, stowed on top of home/ for per-machine files.
HOST ?= $(shell cat /etc/hostname 2>/dev/null)
STOW ?= stow
STOW_FLAGS := --no-folding -d . -t "$(TARGET)"
HOST_STOW = $(STOW) --no-folding -d hosts -t "$(TARGET)"
HAS_HOST = [ -n "$(HOST)" ] && [ -d "hosts/$(HOST)" ]

all: deploy

deploy: check-prereqs
	@bash scripts/deploy.sh "$(DEPLOY_DIR)" "$(TARGET)" "$(HOST)"

install: check-prereqs
	@if [ "$$(realpath -m "$(TARGET)")" = "$$(realpath -m "$(HOME)")" ] && \
	    [ "$$(pwd -P)" != "$$(realpath -m "$(DEPLOY_DIR)")" ]; then \
		echo "Refusing to install this checkout into your home: agents would load unmerged" >&2; \
		echo "edits. Run 'make deploy', or install with TARGET=<dir> to test." >&2; exit 1; fi
	@mkdir -p "$(TARGET)"
	@bash scripts/link-shared.sh clean "$(TARGET)"
	$(STOW) $(STOW_FLAGS) -R home
	@if $(HAS_HOST); then $(HOST_STOW) -R "$(HOST)"; fi
	@bash scripts/link-shared.sh link "$(TARGET)"
	@bash scripts/link-shared.sh record "$(TARGET)"
	@python3 scripts/claude-hooks.py install "$(TARGET)"

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
	@if [ -d "$(TARGET)" ]; then python3 scripts/claude-hooks.py uninstall "$(TARGET)"; fi

check-prereqs:
	@for cmd in stow cksum git python3; do command -v "$$cmd" >/dev/null || { echo "Missing required command: $$cmd" >&2; exit 1; }; done

setup:
	npm install --global ccusage

help:
	@echo "deploy (default) - update DEPLOY_DIR to origin/main and install from it"
	@echo "install          - install this checkout (into your home only from DEPLOY_DIR)"
	@echo "check            - dry-run without changing installed paths"
	@echo "test             - test deployment, scripts and hooks in temporary homes"
	@echo "uninstall        - remove managed links and hooks (run before deleting the checkout)"
	@echo "setup            - install helper tooling (ccusage)"
	@echo "TARGET=, DEPLOY_DIR=, HOST= - override the home, pinned checkout and host"
