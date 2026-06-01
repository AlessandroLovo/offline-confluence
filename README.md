# offline-confluence

A tool for working offline on confluence pages

## Installation

1. Clone this repo, then run `uv sync` from root
2. Make the scripts executable: `chmod +x pull.sh push.sh`
3. Create `~/.atlassian` with two lines: your email, then an API token from https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

1. `./pull.sh <page_url>` — fetches the page and saves it to `pages/{space}/{title}-{id}.html`
2. Edit the local file
3. `./push.sh <path/to/local/page>` — pushes your edits back to Confluence; aborts if the page was updated remotely since your last pull