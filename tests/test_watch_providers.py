import json
import os
from types import SimpleNamespace

from imdbinfo.models import WatchProvider, WatchProviders
from imdbinfo.parsers import parse_watch_providers, _clean_provider_name
from imdbinfo import services

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_json_source")


def load_sample(filename):
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


# --- Model tests ---


def test_watch_provider_model():
    wp = WatchProvider(
        provider_id="amzn1.imdb.w2w.provider.prime_video.ocsfr",
        name="OCS",
        link="https://example.com/watch",
        category="streaming",
        description="with Prime Video Channels",
    )
    assert wp.name == "OCS"
    assert wp.category == "streaming"
    assert wp.description == "with Prime Video Channels"
    assert "OCS" in str(wp)
    assert "streaming" in str(wp)


def test_watch_provider_no_description():
    wp = WatchProvider(
        provider_id="test",
        name="Netflix",
        link="https://example.com",
        category="streaming",
    )
    assert wp.description is None
    assert "Netflix" in str(wp)


def test_watch_providers_model():
    providers = WatchProviders(
        imdbId="tt1375666",
        streaming=[
            WatchProvider(
                provider_id="id1", name="OCS", link="https://a.com",
                category="streaming",
            )
        ],
        rent_buy=[
            WatchProvider(
                provider_id="id2", name="Prime Video", link="https://b.com",
                category="rent_buy", description="from €2.99",
            )
        ],
    )
    assert len(providers.streaming) == 1
    assert len(providers.rent_buy) == 1
    assert "1 streaming" in str(providers)
    assert "1 rent/buy" in str(providers)


def test_watch_providers_empty():
    providers = WatchProviders(imdbId="tt0000000")
    assert providers.streaming == []
    assert providers.rent_buy == []


# --- Provider name cleaning tests ---


def test_clean_provider_name_known():
    assert _clean_provider_name("pvc_ocsfr", "Watch on OCS") == "OCS"
    assert _clean_provider_name("hbomax", "Watch on HBO Max") == "HBO Max"
    assert _clean_provider_name("pvt_aiv", "Watch on Prime Video") == "Prime Video"
    assert _clean_provider_name("amazon", "Search on Amazon") == "Amazon"


def test_clean_provider_name_unknown_strips_prefix():
    assert _clean_provider_name("unknown_tag", "Watch on FooService") == "FooService"
    assert _clean_provider_name("unknown_tag", "Search on BarShop") == "BarShop"


def test_clean_provider_name_unknown_no_prefix():
    assert _clean_provider_name("unknown_tag", "SomeService") == "SomeService"


# --- Parser tests ---


def test_parse_watch_providers_from_sample():
    raw_json = load_sample("sample_watch_providers.json")
    result = parse_watch_providers(raw_json, "1375666")

    assert isinstance(result, WatchProviders)
    assert result.imdbId == "tt1375666"

    # Streaming
    assert len(result.streaming) == 2
    ocs = result.streaming[0]
    assert ocs.name == "OCS"
    assert ocs.provider_id == "amzn1.imdb.w2w.provider.prime_video.ocsfr"
    assert "primevideo.com" in ocs.link
    assert ocs.category == "streaming"

    hbo = result.streaming[1]
    assert hbo.name == "HBO Max"
    assert "play.max.com" in hbo.link

    # Rent/Buy
    assert len(result.rent_buy) == 2
    prime = result.rent_buy[0]
    assert prime.name == "Prime Video"
    assert prime.description == "from €2.99"

    amazon = result.rent_buy[1]
    assert amazon.name == "Amazon"
    assert "amazon.fr" in amazon.link


def test_parse_watch_providers_empty_response():
    raw_json = {"data": {"title": {}}}
    result = parse_watch_providers(raw_json, "0000000")
    assert result.imdbId == "tt0000000"
    assert result.streaming == []
    assert result.rent_buy == []


def test_parse_watch_providers_no_title():
    raw_json = {"data": {}}
    result = parse_watch_providers(raw_json, "0000000")
    assert result.streaming == []
    assert result.rent_buy == []


# --- Service integration test (mocked) ---


def test_get_watch_providers_mocked(monkeypatch):
    sample_json = load_sample("sample_watch_providers.json")

    def mock_get(*args, **kwargs):
        return SimpleNamespace(
            status_code=200,
            json=lambda: sample_json,
            text=json.dumps(sample_json),
        )

    monkeypatch.setattr(services.niquests, "get", mock_get)
    result = services.get_watch_providers("tt1375666")

    assert isinstance(result, WatchProviders)
    assert result.imdbId == "tt1375666"
    assert len(result.streaming) == 2
    assert len(result.rent_buy) == 2
    assert result.streaming[0].name == "OCS"
