"""
integration tests for mac_service
"""

import plistlib

import pytest

import salt.utils.files

pytestmark = [
    pytest.mark.slow_test,
    pytest.mark.skip_if_binaries_missing("launchctl", "plutil"),
    pytest.mark.skip_unless_on_darwin,
]


@pytest.fixture(scope="function")
def setup_teardown_vars(salt_call_cli):

    SERVICE_NAME = "com.salt.integration.test"
    SERVICE_PATH = "/Library/LaunchDaemons/com.salt.integration.test.plist"

    service_data = {
        "KeepAlive": True,
        "Label": SERVICE_NAME,
        "ProgramArguments": ["/bin/sleep", "1000"],
        "RunAtLoad": True,
    }
    with salt.utils.files.fopen(SERVICE_PATH, "wb") as fp:
        plistlib.dump(service_data, fp)
    salt_call_cli.run("service.enable", SERVICE_NAME)
    salt_call_cli.run("service.start", SERVICE_NAME)

    try:
        yield SERVICE_NAME
    finally:
        salt_call_cli.run("service.stop", SERVICE_NAME)
        salt.utils.files.safe_rm(SERVICE_PATH)


def test_show(salt_call_cli, setup_teardown_vars):
    """
    Test service.show
    """
    SERVICE_NAME = setup_teardown_vars[0]
    # Existing Service
    service_info = salt_call_cli.run("service.show", [SERVICE_NAME])
    assert isinstance(service_info, dict)
    assert service_info["plist"]["Label"] == SERVICE_NAME

    # Missing Service
    assert "Service not found" in salt_call_cli.run("service.show", "spongebob")


def test_launchctl(salt_call_cli):
    """
    Test service.launchctl
    """
    # Expected Functionality
    assert salt_call_cli.run("service.launchctl", "error", "bootstrap", 64)
    assert (
        salt_call_cli.run(
            "service.launchctl", ["error", "bootstrap", 64], return_stdout=True
        )
        == "64: unknown error code"
    )

    # Raise an error
    assert "Failed to error service" in salt_call_cli.run(
        "service.launchctl", "error", "bootstrap"
    )


def test_list(salt_call_cli, setup_teardown_vars):
    """
    Test service.list
    """
    SERVICE_NAME = setup_teardown_vars[0]
    # Expected Functionality
    assert "PID" in salt_call_cli.run("service.list")
    assert "{" in salt_call_cli.run("service.list", SERVICE_NAME)

    # Service not found
    assert "Service not found" in salt_call_cli.run("service.list", "spongebob")


def test_enable(salt_call_cli, setup_teardown_vars):
    """
    Test service.enable
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.enable", SERVICE_NAME)

    assert "Service not found" in salt_call_cli.run("service.enable", "spongebob")


def test_disable(salt_call_cli, setup_teardown_vars):
    """
    Test service.disable
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.disable", SERVICE_NAME)

    assert "Service not found" in salt_call_cli.run("service.disable", "spongebob")


def test_start(salt_call_cli, setup_teardown_vars):
    """
    Test service.start
    Test service.stop
    Test service.status
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.start", SERVICE_NAME)

    assert "Service not found" in salt_call_cli.run("service.start", "spongebob")


def test_stop(salt_call_cli, setup_teardown_vars):
    """
    Test service.stop
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.stop", SERVICE_NAME)

    assert "Service not found" in salt_call_cli.run("service.stop", ["spongebob"])


def test_status(salt_call_cli, setup_teardown_vars):
    """
    Test service.status
    """
    SERVICE_NAME = setup_teardown_vars[0]
    # A running service
    assert salt_call_cli.run("service.start", SERVICE_NAME)
    assert salt_call_cli.run("service.status", SERVICE_NAME)

    # A stopped service
    assert salt_call_cli.run("service.stop", SERVICE_NAME)
    assert not salt_call_cli.run("service.status", SERVICE_NAME)

    # Service not found
    assert not salt_call_cli.run("service.status", "spongebob")


def test_available(salt_call_cli, setup_teardown_vars):
    """
    Test service.available
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.available", SERVICE_NAME)
    assert not salt_call_cli.run("service.available", "spongebob")


def test_missing(salt_call_cli, setup_teardown_vars):
    """
    Test service.missing
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert not salt_call_cli.run("service.missing", SERVICE_NAME)
    assert salt_call_cli.run("service.missing", "spongebob")


def test_enabled(salt_call_cli, setup_teardown_vars):
    """
    Test service.enabled
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.enabled", SERVICE_NAME)
    assert salt_call_cli.run("service.start", SERVICE_NAME)

    assert salt_call_cli.run("service.enabled", SERVICE_NAME)
    assert salt_call_cli.run("service.stop", SERVICE_NAME)

    assert salt_call_cli.run("service.enabled", "spongebob")


def test_disabled(salt_call_cli, setup_teardown_vars):
    """
    Test service.disabled
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.start", SERVICE_NAME)
    assert not salt_call_cli.run("service.disabled", SERVICE_NAME)

    assert salt_call_cli.run("service.disable", SERVICE_NAME)
    assert salt_call_cli.run("service.disabled", SERVICE_NAME)
    assert salt_call_cli.run("service.enable", SERVICE_NAME)
    assert "Service not found" in salt_call_cli.run("service.stop", "spongebob")


def test_get_all(salt_call_cli, setup_teardown_vars):
    """
    Test service.get_all
    """
    SERVICE_NAME = setup_teardown_vars[0]
    services = salt_call_cli.run("service.get_all")
    assert isinstance(services, list)
    assert SERVICE_NAME in services


def test_get_enabled(salt_call_cli, setup_teardown_vars):
    """
    Test service.get_enabled
    """
    SERVICE_NAME = setup_teardown_vars[0]
    services = salt_call_cli.run("service.get_enabled")
    assert isinstance(services, list)
    assert SERVICE_NAME in services


def test_service_laoded(salt_call_cli, setup_teardown_vars):
    """
    Test service.get_enabled
    """
    SERVICE_NAME = setup_teardown_vars[0]
    assert salt_call_cli.run("service.loaded", SERVICE_NAME)
