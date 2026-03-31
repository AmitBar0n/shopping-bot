import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_config_loads_required_vars(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("AMIT_ID", "111")
    monkeypatch.setenv("PARTNER_ID", "222")
    monkeypatch.setenv("AMIT_NAME", "עמית")
    monkeypatch.setenv("PARTNER_NAME", "ירדן")

    import importlib
    import config as cfg
    importlib.reload(cfg)

    assert cfg.BOT_TOKEN == "test_token"
    assert cfg.AMIT_ID == 111
    assert cfg.PARTNER_ID == 222
    assert cfg.AMIT_NAME == "עמית"
    assert cfg.PARTNER_NAME == "ירדן"
    assert cfg.AUTHORIZED_IDS == {111, 222}
