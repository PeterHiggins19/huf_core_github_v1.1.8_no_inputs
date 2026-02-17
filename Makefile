.PHONY: help fetch-data fetch-markham fetch-toronto planck-guide fetch-toronto-yes bootstrap

help:
	@echo "Targets:"
	@echo "  fetch-data     Download Markham + Toronto inputs (Planck is manual)"
	@echo "  fetch-markham  Download Markham 2018 budget workbook"
	@echo "  fetch-toronto  Download Toronto traffic signal phase-status CSV"
	@echo "  planck-guide   Print guided/manual Planck download steps"
	@echo "  fetch-toronto-yes  Download Toronto traffic CSV (non-interactive selection)"
	@echo "  bootstrap      Create venv + install deps (cross-platform)"

fetch-data:
	python scripts/fetch_data.py --markham --toronto

fetch-markham:
	python scripts/fetch_data.py --markham

fetch-toronto:
	python scripts/fetch_data.py --toronto

planck-guide:
	python scripts/fetch_data.py --planck-guide

fetch-toronto-yes:
	python scripts/fetch_data.py --toronto --yes

bootstrap:
	python scripts/bootstrap.py
