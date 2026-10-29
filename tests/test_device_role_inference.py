from netbox_unifi_sync.services import sync_engine


def test_legacy_switch_without_features_is_lan():
    # Legacy stat/device payloads have no "features" list; switches carry type "usw".
    device = {"type": "usw", "model": "USPM48P", "name": "USW Pro Max 48 PoE"}
    assert sync_engine.infer_role_key_for_device(device) == "LAN"


def test_integration_switch_features_still_lan():
    device = {"model": "USW-Pro-Max-48-PoE", "features": ["switching"]}
    assert sync_engine.infer_role_key_for_device(device) == "LAN"


def test_legacy_gateway_still_gateway():
    device = {"type": "udm", "model": "UDMPROMAX"}
    assert sync_engine.infer_role_key_for_device(device) == "GATEWAY"


def test_legacy_modem_stays_unknown():
    device = {"type": "uci", "model": "UCI"}
    assert sync_engine.infer_role_key_for_device(device) == "UNKNOWN"
