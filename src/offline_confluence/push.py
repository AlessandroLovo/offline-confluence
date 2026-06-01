import json
import re
import sys
from pathlib import Path

from offline_confluence.auth import load_credentials
from offline_confluence.confluence import ConfluenceClient
from offline_confluence.format import compact, prettify

META_PATTERN = re.compile(r"<!--\s*confluence-meta:\s*(\{.*?\})\s*-->", re.DOTALL)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: push <path/to/local/page>", file=sys.stderr)
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    raw = filepath.read_text(encoding="utf-8")
    match = META_PATTERN.search(raw)
    if not match:
        print("No confluence-meta comment found. Was this file created with `pull`?", file=sys.stderr)
        sys.exit(1)

    meta = json.loads(match.group(1))
    page_id = meta["page_id"]
    base_url = meta["base_url"]
    title = meta["title"]

    pretty_body = META_PATTERN.sub("", raw).lstrip("\n")
    body = compact(pretty_body)

    email, token = load_credentials()
    client = ConfluenceClient(base_url, email, token)

    current = client.get_page(page_id)
    local_version = meta.get("version")
    if local_version is not None and current["version_number"] != local_version:
        print(
            f"Aborted: page was updated remotely (local version {local_version}, "
            f"remote version {current['version_number']}). Re-pull before pushing.",
            file=sys.stderr,
        )
        sys.exit(1)
    new_version = current["version_number"] + 1
    client.update_page(page_id, title, body, new_version)

    meta["version"] = new_version
    updated_meta = json.dumps(meta)
    filepath.write_text(f"<!-- confluence-meta: {updated_meta} -->\n{prettify(body)}", encoding="utf-8")
    print(f"Updated '{title}' to version {new_version}.")


if __name__ == "__main__":
    main()
