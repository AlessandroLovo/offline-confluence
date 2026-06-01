import json
import pathlib
import re
import sys
from urllib.parse import urlparse

from auth import load_credentials
from confluence import ConfluenceClient


def parse_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    match = re.search(r"/pages/(\d+)", parsed.path)
    if not match:
        raise RuntimeError(f"Cannot extract page ID from URL: {url}\nExpected a URL like .../pages/123456789/...")
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    return base_url, match.group(1)


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python pull <page_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    base_url, page_id = parse_url(url)

    email, token = load_credentials()
    client = ConfluenceClient(base_url, email, token)
    page = client.get_page(page_id)

    meta = json.dumps({"page_id": page["id"], "base_url": base_url, "title": page["title"]})
    content = f"<!-- confluence-meta: {meta} -->\n{page['body_storage']}"

    pages_dir = pathlib.Path("pages")
    pages_dir.mkdir(exist_ok=True)
    filename = pages_dir / f"{page_id}_{slugify(page['title'])}.html"
    filename.write_text(content, encoding="utf-8")
    print(f"Saved: {filename}")


if __name__ == "__main__":
    main()
