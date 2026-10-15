# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WijnVoorraadApp ("Wine Inventory App") is a Django web application for managing personal wine cellars. It tracks wine stock, receipts (ontvangsten), inventory mutations, reservations, and orders (bestellingen). The application is in Dutch.

## Commands

**Always run Python tooling through Poetry** (`poetry run ...`), which uses the in-project virtualenv at `.venv` (`poetry.toml` sets `in-project = true`). Never use a global `python`, `pytest`, `pip`, etc., and never install packages outside Poetry (`poetry add` / `poetry install`).

### Development

```bash
# Install dependencies
poetry install

# Run development server
poetry run python manage.py runserver --settings=WijnProject.settings.dev

# Apply migrations
poetry run python manage.py migrate --settings=WijnProject.settings.dev

# Create new migration
poetry run python manage.py makemigrations --settings=WijnProject.settings.dev

# Collect static files (production)
poetry run python manage.py collectstatic --settings=WijnProject.settings.prod
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov

# Run a single test file
poetry run pytest WijnVoorraad/tests/models/test_voorraadmutatie.py

# Run a specific test
poetry run pytest WijnVoorraad/tests/models/test_voorraadmutatie.py::TestClass::test_method
```

pytest uses `WijnProject.settings.dev` (configured in `pytest.ini`). The dev settings use SQLite (`db.sqlite3` in the repo root, which is tracked in git).

Tests live in `WijnVoorraad/tests/models/` and `WijnVoorraad/tests/views/`. Model tests share fixtures through `SharedTestDataMixin` in `tests/models/model_helper.py`. View tests that touch OpenAI must patch `WijnVoorraad.views.OpenAI` so no paid call is made.

### Environment / secrets

`base.py` calls `config("DB_PASSWORD")` and `config("OPENAI_API_KEY")` with no default, and `prod.py` also requires `SECRET_KEY`. `python-decouple` reads these from the environment or from the gitignored `WijnProject/settings/.env`. Without them, importing settings (and therefore pytest) fails.

### Linting

```bash
# Lint Python
poetry run pylint WijnVoorraad WijnProject

# Lint templates
poetry run djlint WijnVoorraad/templates --check
```

### Versioning & Releases

```bash
# Bump version (uses commitizen, updates CHANGELOG.md, triggers build/push_all.cmd)
poetry run cz bump
```

Commitizen is configured to use conventional commits. Version is stored in `pyproject.toml` and `WijnProject/__init__.py`. The `[tool.commitizen]` section in `pyproject.toml` is the live config; `.cz.toml` is a stale leftover (still says 0.16.0) and `pyproject.toml`'s `pre_bump_hooks` references a `make_requirements.cmd` that is not in the repo. The post-bump hook (`build/push_all.cmd`) pushes tags. Production deployment is done with the shell scripts in `build/` (e.g. `install.sh <app> <tag>`), run on the host against a tagged release.

## Architecture

### Django Project Structure

- **`WijnProject/`** — Django project config
  - `settings/base.py` — shared settings; reads `DB_PASSWORD` and `OPENAI_API_KEY` from environment via `python-decouple`
  - `settings/dev.py` — SQLite, `DEBUG=True`
  - `settings/prod.py` — SQLite, `DEBUG=False`, hosted at `vino.vdwaal.net`
  - `urls.py` — routes to `WijnVoorraad.urls`, Django admin, auth, and django-select2

- **`WijnVoorraad/`** — single Django app containing all business logic

### Key Models (`models.py`)

The inventory system is built around this core chain:

```
WijnSoort (wine type) ←── Wijn (wine) ←── Ontvangst (receipt) ←── VoorraadMutatie (mutation)
                                                                          ↓
                                                                   WijnVoorraad (stock)
```

- **`Wijn`** — a wine record (domain, name, year, type, grape varieties)
- **`Ontvangst`** — a purchase/receipt event linking a `Deelnemer` (participant) to a `Wijn`
- **`VoorraadMutatie`** — stock mutation (IN/OUT) with action types: Koop, Ontvangst, Verplaatsing, Drink, Afboeking
- **`WijnVoorraad`** — denormalized stock table, automatically maintained by `VoorraadMutatie.save()`/`delete()` via `WijnVoorraad.Bijwerken()`
- **`Locatie`** + **`Vak`** — storage locations and slots within them
- **`Deelnemer`** — participant/member, linked to Django `User` via M2M
- **`Bestelling`** + **`BestellingRegel`** — orders for picking wine from a location; support reservation logic via `WijnVoorraad.aantal_rsv`
- **`AIUsage`** — tracks OpenAI API calls

**Critical invariant**: `WijnVoorraad.aantal` must equal sum of IN mutations minus sum of OUT mutations. `WijnVoorraadService.ControleerLocatie/ControleerOntvangst` verify this. `WijnVoorraadService.BijwerkenVrdOntvangst` can recalculate and repair the stock table from mutations.

Behaviors that are easy to break:

- Stock is a "stock row per (ontvangst, locatie, vak)". Editing or deleting a `VoorraadMutatie` first reverses the old mutation, then applies the new one (`WijnVoorraad.Bijwerken`). A stock row that reaches 0 is deleted, and `Wijn.check_afsluiten()` then sets or clears `datumAfgesloten`. So rows with `aantal == 0` should never exist.
- Validation lives in `clean()`, not `save()`. `VoorraadMutatie.clean()` calls `WijnVoorraad.check_voorraad_wijziging` (rejects negative stock) and `BestellingRegel.clean()` calls `check_voorraad_rsv` (rejects over-reservation). Programmatic callers must call `clean()` themselves; the `drinken` and `afboeken` helpers do, but `verplaatsen` and `voorraad_plus_1` do not.
- `VoorraadMutatie.drinken/verplaatsen/afboeken/voorraad_plus_1` are the static factory methods for creating mutations. A move (`verplaatsen`) is two mutations, one UIT at the old location and one IN at the new one, both with action `V`.
- Reservations: `BestellingRegel.save()/delete()` maintain `WijnVoorraad.aantal_rsv` through `Bijwerken_rsv`, but only for lines with `verwerkt == "N"`. `aantal_werkelijk` (the `aantal_correctie` if set, else `aantal`) is the number used everywhere. Once a line is processed (`A` afgeboekt / `V` verplaatst) it can't go back to `N`. Saving a line also calls `Bestelling.check_afsluiten()`.
- Model method names mix Dutch and English, and some use PascalCase (`Bijwerken`, `ControleerLocatie`); follow the existing name when calling or extending them.

### Views Organization

- **`views.py`** — main views: inventory list/detail, mutations, orders, AI wine search (OpenAI integration)
- **`views_basis.py`** — master data views: Gebruiker, WijnSoort, DruivenSoort, Locatie, Vak, Deelnemer
- **`views_popup.py`** — popup views used by django-select2 inline creation

### Session-Based Filtering (`wijnvars.py`)

All list views use session-stored filters (deelnemer, locatie, wijnsoort, fuzzy text search, sorting). The `wijnvars.py` module manages reading/writing these session variables and provides context helpers used across views.

### Services (`services.py`)

`WijnVoorraadService` provides stock integrity verification and repair operations, separate from the model layer.

### Templates

Templates are under `WijnVoorraad/templates/WijnVoorraad/`. Base template: `base.html`. The app uses custom CSS classes per wine type (`wijnsoort_rood`, `wijnsoort_wit`, etc.) for color-coding in the UI.

### External Integrations

- **OpenAI** — used in the AI wine search feature (`AIview` in `views.py`, URL name `WijnVoorraad:AI-zoeken`): a two-step Responses API flow (read the label image, then enrich via web search) with the model named in `settings.OPENAI_MODEL` (override via `OPENAI_MODEL` in `.env`; default `gpt-6.1-sol`), structured output via Pydantic models (`WineLabelReading`, `WineInfo`), and usage tracked in `AIUsage`. Every call costs money, so the view requires login and must refuse anonymous requests before any OpenAI client is created.
- **django-select2** — for autocomplete fields in forms
- **translate** — for translating wine type names to Dutch
