from types import SimpleNamespace

from netbox_unifi_sync.services import sync_engine

CLIENT = {
    "mac": "AA:BB:CC:DD:EE:FF",
    "hostname": "iphone-01",
    "ip": "10.0.0.25",
    "ssid": "Corp WiFi",
    "ap_name": "AP-01",
    "signal": -62,
    "last_seen": 1710000000.8,
    "connected_at": "2026-04-19T09:15:00Z",
}
PORT = {"poe_power": "4.34"}


def test_readings_on_by_default(monkeypatch):
    monkeypatch.delenv("SYNC_LIVE_READINGS", raising=False)
    assert sync_engine._sync_live_readings() is True
    assert "Signal: -62dBm" in sync_engine._client_description(CLIENT)
    assert "PoE draw" in sync_engine._build_port_description(PORT, poe="auto")


def test_readings_off_keeps_stable_client_fields_only(monkeypatch):
    monkeypatch.setenv("SYNC_LIVE_READINGS", "false")
    assert sync_engine._client_description(CLIENT) == (
        "unifi-client:AA:BB:CC:DD:EE:FF | UniFi client: iphone-01 | "
        "IP: 10.0.0.25 | SSID: Corp WiFi"
    )


def test_readings_off_drops_poe_draw_and_utilization(monkeypatch):
    monkeypatch.setenv("SYNC_LIVE_READINGS", "false")
    assert sync_engine._build_port_description(PORT, poe="auto", speed_mbps=2500) == (
        "PoE: auto | Max speed: 2500Mbps"
    )
    radio = sync_engine._build_radio_description({"band": "na", "channel": 36, "utilization": 12})
    assert "Utilization" not in radio
    assert "Channel: 36" in radio


def test_readings_off_skips_uptime_and_last_seen(monkeypatch):
    monkeypatch.setenv("SYNC_LIVE_READINGS", "false")
    monkeypatch.setattr(sync_engine, "ensure_custom_field", lambda *a, **k: None)
    saved = []
    nb_device = SimpleNamespace(
        name="sw1",
        custom_fields={"unifi_firmware": "1.0", "unifi_mac": "aa", "unifi_uptime": 5, "unifi_last_seen": "x"},
        save=lambda: saved.append(True),
    )
    sync_engine.sync_device_custom_fields(
        None, nb_device, {"version": "1.0", "mac": "aa", "uptime": 999, "last_seen": 1710000000}
    )
    assert saved == []

    sync_engine.sync_device_custom_fields(
        None, nb_device, {"version": "2.0", "mac": "aa", "uptime": 999, "last_seen": 1710000000}
    )
    assert saved == [True]
    assert nb_device.custom_fields["unifi_firmware"] == "2.0"
    assert nb_device.custom_fields["unifi_uptime"] == 5
