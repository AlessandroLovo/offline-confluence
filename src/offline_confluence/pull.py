import json
import pathlib
import re
import sys
from urllib.parse import urlparse

from offline_confluence.auth import load_credentials
from offline_confluence.confluence import ConfluenceClient


def parse_url(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url)
    match = re.search(r"/spaces/([^/]+)/pages/(\d+)", parsed.path)
    if not match:
        raise RuntimeError(f"Cannot extract space/page ID from URL: {url}\nExpected a URL like .../spaces/SPACE/pages/123456789/...")
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    return base_url, match.group(1), match.group(2)


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: pull <page_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    base_url, space_key, page_id = parse_url(url)

    email, token = load_credentials()
    client = ConfluenceClient(base_url, email, token)
    page = client.get_page(page_id)

    meta = json.dumps({"page_id": page["id"], "base_url": base_url, "title": page["title"], "version": page["version_number"]})
    content = f"<!-- confluence-meta: {meta} -->\n{page['body_storage']}"

    space_dir = pathlib.Path("pages") / space_key
    space_dir.mkdir(parents=True, exist_ok=True)
    filename = space_dir / f"{slugify(page['title'])}-{page_id}.html"
    filename.write_text(content, encoding="utf-8")
    print(f"Saved: {filename}")


if __name__ == "__main__":
    main()
