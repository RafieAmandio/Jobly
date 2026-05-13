from jobly.i18n.strings import t


def test_t_returns_indonesian():
    result = t("welcome", "id")
    assert "Selamat datang" in result


def test_t_returns_english():
    result = t("welcome", "en")
    assert "Welcome" in result


def test_t_with_kwargs():
    result = t("credits_balance", "en", balance=10)
    assert "10" in result


def test_t_missing_key():
    result = t("nonexistent_key", "id")
    assert "[missing:" in result


def test_t_defaults_to_indonesian():
    result = t("welcome")
    assert "Selamat datang" in result


def test_all_keys_have_both_languages():
    from jobly.i18n.strings import STRINGS

    for key, translations in STRINGS.items():
        assert "id" in translations, f"Key '{key}' missing Indonesian translation"
        assert "en" in translations, f"Key '{key}' missing English translation"
