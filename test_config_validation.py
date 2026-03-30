import json
import pytest
import os


def test_config_file_validity():
    """Validate that a usable config file exists and contains required fields.

    This test will be skipped when no local or example config is present. It
    uses assert statements (no return values) so pytest emits no warnings.
    """
    config = None
    for config_file in ("gmail_config_local.json", "gmail_config_example.json"):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            pytest.skip(f"{config_file} exists but is not valid JSON")

        # If the example file contains placeholder credentials, skip it
        if config.get("username") == "your-email@gmail.com":
            pytest.skip(f"{config_file} is an example file; provide real credentials to run this test")

        # We found a candidate config file
        break

    if not config:
        pytest.skip("No configuration file found (gmail_config_local.json or gmail_config_example.json)")

    # Required fields
    for field in ("username", "app_password", "email_filters"):
        assert field in config and config[field], f"Missing or empty required field: {field}"

    # email_filters must be a mapping
    assert isinstance(config["email_filters"], dict), "email_filters must be an object/dictionary"
