from types import SimpleNamespace

from netbox_unifi_sync.services.unifi.client import Client


def _site():
    return SimpleNamespace(name="default", api_id="default", desc="Default")


def test_legacy_client_endpoint_lists_connected_clients():
    # stat/user requires a MAC (api.err.IdRequired); stat/sta lists connected clients.
    client = Client(SimpleNamespace(api_style="legacy"), _site())
    assert client._build_url() == "/api/s/default/stat/sta"


def test_integration_client_endpoint_unchanged():
    client = Client(SimpleNamespace(api_style="integration"), _site())
    assert client._build_url() == "/sites/default/clients"
