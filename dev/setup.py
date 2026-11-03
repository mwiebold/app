"""Create ignored local settings from upstream's template without overwriting them."""

from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    target = root / "api/cora/setting.php"
    if target.exists():
        print("Keeping existing api/cora/setting.php")
        return

    settings = (root / "api/cora/setting.example.php").read_text()
    replacements = {
        "'commit' => null": "'commit' => 'local'",
        "'beestat_api_key_local' => ''": "'beestat_api_key_local' => '0000000000000000000000000000000000000001'",
        "'ecobee_api_key_local' => ''": "'ecobee_api_key_local' => '0000000000000000000000000000000000000002'",
        "'beestat_root_uri' => ''": "'beestat_root_uri' => 'http://localhost:8088/'",
        "'database_host' => ''": "'database_host' => 'db'",
        "'database_username' => ''": "'database_username' => 'beestat'",
        "'database_password' => ''": "'database_password' => 'beestat-local-only'",
        "'database_name' => ''": "'database_name' => 'beestat'",
        "'force_ssl' => true": "'force_ssl' => false",
    }
    for original, replacement in replacements.items():
        if settings.count(original) != 1:
            raise ValueError(f"Upstream settings template changed: {original}")
        settings = settings.replace(original, replacement)

    with target.open("x") as output:
        output.write(settings)
    # Apache's container user must be able to read the bind-mounted file.
    target.chmod(0o644)
    print("Created api/cora/setting.php for the local Docker environment")


if __name__ == "__main__":
    main()
