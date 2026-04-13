from speaker import split_sentences


def test_splits_on_chinese_period():
    assert split_sentences("你好。世界。") == ["你好", "世界"]


def test_splits_on_english_period():
    assert split_sentences("Hello. World.") == ["Hello", "World"]


def test_splits_on_exclamation():
    assert split_sentences("Good！Great!") == ["Good", "Great"]


def test_splits_on_question():
    assert split_sentences("Why？Really?") == ["Why", "Really"]


def test_splits_on_newline():
    assert split_sentences("Line one\nLine two") == ["Line one", "Line two"]


def test_strips_empty_strings():
    assert split_sentences("Hello.\n\nWorld.") == ["Hello", "World"]


def test_mixed_language():
    result = split_sentences("Hello. 你好。")
    assert result == ["Hello", "你好"]


def test_empty_string():
    assert split_sentences("") == []


def test_no_delimiters():
    assert split_sentences("Hello world") == ["Hello world"]
