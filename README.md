# offline-confluence

A tool for working offline on confluence pages

## Installation

- Clone this repo, then run `uv sync` from root
- Obtain an Atlassian API token from https://id.atlassian.com/manage-profile/security/api-tokens, and paste it in `~/.atlassian`

## Usage

1. `uv run python pull <page url>`: this pulls the page html from Confluence, and stores it in `pages/`
2. Edit your page
3. `uv run python push <path/to/local/page>`: this pushes your edits back to confluence, updating page version