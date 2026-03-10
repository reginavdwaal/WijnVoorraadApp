# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WijnVoorraadApp ("Wine Inventory App") is a Django web application for managing personal wine cellars. It tracks wine stock, receipts (ontvangsten), inventory mutations, reservations, and orders (bestellingen). The application is in Dutch.

## Commands

### Development

```bash
# Install dependencies
poetry install

# Run development server
python manage.py runserver --settings=WijnProject.settings.dev

# Apply migrations
python manage.py migrate --settings=WijnProject.settings.dev

# Create new migration
python manage.py makemigrations --settings=WijnProject.settings.dev

# Collect static files (production)
python manage.py collectstatic --settings=WijnProject.settings.prod
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov

# Run a single test file
pytest WijnVoorraad/tests_something.py

# Run a specific test
pytest WijnVoorraad/tests_something.py::TestClass::test_method
```

pytest uses `WijnProject.settings.dev` (configured in `pytest.ini`). The dev settings use SQLite.

### Linting

```bash
# Lint Python
pylint WijnVoorraad WijnProject

# Lint templates
djlint WijnVoorraad/templates --check
```

### Versioning & Releases

```bash
# Bump version (uses commitizen, updates CHANGELOG.md, triggers build/push_all.cmd)
cz bump
```

Commitizen is configured to use conventional commits. Version is stored in `pyproject.toml` and `WijnProject/__init__.py`.

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

- **OpenAI** — used in the AI wine search feature to parse wine labels; model and response usage tracked in `AIUsage`
- **django-select2** — for autocomplete fields in forms
- **translate** — for translating wine type names to Dutch
