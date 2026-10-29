from types import SimpleNamespace

from netbox_unifi_sync.services import sync_engine


class _Types:
    def __init__(self, types):
        self.types = types

    def filter(self, **kwargs):
        return [t for t in self.types if t.manufacturer_id == kwargs.get("manufacturer_id")]

    def get(self, **kwargs):
        hits = [t for t in self.types
                if t.model == kwargs.get("model") and t.manufacturer_id == kwargs.get("manufacturer_id")]
        return hits[0] if hits else None


def _nb(*types):
    return SimpleNamespace(dcim=SimpleNamespace(device_types=_Types(list(types))))


UBNT = SimpleNamespace(id=1)


def _type(model, part_number, manufacturer_id=1):
    return SimpleNamespace(model=model, part_number=part_number, manufacturer_id=manufacturer_id)


def test_library_type_found_by_part_number_despite_product_name_model():
    library = _type("UniFi Switch Pro Max 48 PoE", "USW-Pro-Max-48-PoE")
    found, curated = sync_engine.find_device_type(_nb(library), UBNT, "USPM48P")
    assert found is library
    assert curated is True


def test_part_number_match_ignores_case_and_separators():
    library = _type("UniFi Dream Machine Pro Max", "UDM-PRO-MAX")
    flex = _type("UniFi Switch Flex Mini 2.5G", "USW-Flex-2-5G-5")
    nb = _nb(library, flex)
    assert sync_engine.find_device_type(nb, UBNT, "UDMPROMAX")[0] is library
    assert sync_engine.find_device_type(nb, UBNT, "USWED35")[0] is flex


def test_library_type_preferred_over_code_named_type():
    plugin_made = _type("USPM48P", "USW-Pro-Max-48-PoE")
    library = _type("UniFi Switch Pro Max 48 PoE", "USW-Pro-Max-48-PoE")
    found, curated = sync_engine.find_device_type(_nb(plugin_made, library), UBNT, "USPM48P")
    assert found is library and curated is True


def test_code_named_type_still_found_and_not_curated():
    plugin_made = _type("USPM48P", "USW-Pro-Max-48-PoE")
    found, curated = sync_engine.find_device_type(_nb(plugin_made), UBNT, "USPM48P")
    assert found is plugin_made and curated is False


def test_unknown_code_falls_back_to_model_match():
    plugin_made = _type("XYZ123", "")
    found, curated = sync_engine.find_device_type(_nb(plugin_made), UBNT, "XYZ123")
    assert found is plugin_made and curated is False


def test_other_manufacturers_are_ignored():
    other = _type("UniFi Switch Pro Max 48 PoE", "USW-Pro-Max-48-PoE", manufacturer_id=2)
    found, _ = sync_engine.find_device_type(_nb(other), UBNT, "USPM48P")
    assert found is None
