.PHONY: run lint clean

PYTHON  = venv\Scripts\python.exe
RUFF    = venv\Scripts\ruff.exe
SCRIPTS = Scripts
DB      = data\processed\data.db

ARCHIVOS = \
	$(SCRIPTS)\models.py \
	$(SCRIPTS)\database.py \
	$(SCRIPTS)\scraper.py \
	$(SCRIPTS)\seed.py \
	$(SCRIPTS)\queries.py \
	$(SCRIPTS)\main.py

run:
	cd $(SCRIPTS) && ..\$(PYTHON) main.py

lint:
	$(RUFF) check $(ARCHIVOS)

clean:
	del /f $(DB)