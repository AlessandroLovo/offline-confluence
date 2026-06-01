import requests


class ConfluenceClient:
    def __init__(self, base_url: str, email: str, token: str):
        self._base = base_url.rstrip("/") + "/wiki/rest/api"
        self._auth = (email, token)

    def _check(self, resp: requests.Response) -> None:
        if resp.status_code == 401:
            raise RuntimeError("Authentication failed. Check your email and API token in ~/.atlassian.")
        if resp.status_code == 404:
            raise RuntimeError(f"Page not found (404).")
        if resp.status_code == 409:
            raise RuntimeError("Version conflict (409): the page was modified remotely. Re-pull before pushing.")
        if not resp.ok:
            raise RuntimeError(f"Confluence API error {resp.status_code}: {resp.text}")

    def get_page(self, page_id: str) -> dict:
        resp = requests.get(
            f"{self._base}/content/{page_id}",
            params={"expand": "body.storage,version"},
            auth=self._auth,
        )
        self._check(resp)
        data = resp.json()
        return {
            "id": data["id"],
            "title": data["title"],
            "version_number": data["version"]["number"],
            "body_storage": data["body"]["storage"]["value"],
        }

    def update_page(self, page_id: str, title: str, body_storage: str, new_version: int) -> None:
        resp = requests.put(
            f"{self._base}/content/{page_id}",
            auth=self._auth,
            json={
                "version": {"number": new_version},
                "title": title,
                "type": "page",
                "body": {"storage": {"value": body_storage, "representation": "storage"}},
            },
        )
        self._check(resp)
