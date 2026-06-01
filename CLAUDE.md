# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`offline-confluence` is a Python CLI tool that lets users pull Confluence pages as HTML, edit them locally, and push changes back to Confluence with automatic version bumping.

## Setup

- **Python version:** 3.13+ (managed via `uv`)
- **Install dependencies:** `uv sync`
- **Atlassian API token:** must be stored at `~/.atlassian` (plain text)

## Commands

```bash
uv run python pull <page_url>        # fetch page HTML into pages/
uv run python push <path/to/page>    # push edits back to Confluence
```

## Architecture

Four files at the repo root:

- `auth.py` — reads `~/.atlassian` (two lines: email, API token) and returns `(email, token)`
- `confluence.py` — `ConfluenceClient(base_url, email, token)` with `get_page(page_id)` and `update_page(...)`; raises `RuntimeError` with human-readable messages on API errors
- `pull.py` — parses the page URL to extract `base_url`, space key, and `page_id`, fetches the page's storage-format body, prepends a `<!-- confluence-meta: {...} -->` comment, and writes to `pages/{space_key}/{title_slug}-{page_id}.html`
- `push.py` — reads the local file, extracts the metadata comment (page_id, base_url, title), strips it from the body, re-fetches the current version number from the API, and calls `update_page` with `version + 1`

Pages are stored in Confluence storage format (XHTML-like) so they round-trip without conversion. The metadata comment is the only mechanism linking a local file back to its remote page.

When adding dependencies, use `uv add <package>` — do not edit `pyproject.toml` manually.
