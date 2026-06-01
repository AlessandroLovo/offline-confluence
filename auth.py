import pathlib


def load_credentials() -> tuple[str, str]:
    path = pathlib.Path.home() / ".atlassian"
    if not path.exists():
        raise RuntimeError(
            f"~/.atlassian not found. Create it with two lines: your email, then your API token.\n"
            "Get a token at https://id.atlassian.com/manage-profile/security/api-tokens"
        )
    lines = path.read_text().strip().splitlines()
    if len(lines) < 2:
        raise RuntimeError("~/.atlassian must contain two lines: email, then API token.")
    return lines[0].strip(), lines[1].strip()
