# SRD Monster Query API

Local-first API and CLI for querying the supplied D&D 5e SRD monster dataset in natural language.

## Quick start

1. Create `.env` from `.env.example` and start PostgreSQL with `docker compose up -d db`.
2. Install with `py -m pip install -e ".[dev]"`.
3. Run `alembic upgrade head`, then `python -m app.importer`.
4. Start the API: `uvicorn app.main:app --reload`.
5. Query it: `monster-query query "medium undead CR 5 or lower immune to poison"`.

Ollama is optional. Start it locally and set `OLLAMA_ENABLED=true` to let it translate queries that the rule parser cannot fully interpret.

## Licence and attribution

This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License available at https://creativecommons.org/licenses/by/4.0/legalcode.

Dataset acquisition source: https://gist.github.com/tkfu/9819e4ac6d529e225e9fc58b358c3479

Image URLs in the source file are retained as metadata but are not downloaded, served, or asserted to be licensed by this project.
