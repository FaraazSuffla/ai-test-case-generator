"""Tests for src/generator.py."""

import pytest
from unittest.mock import MagicMock, patch

from src.analyzer import PageAnalysis
from src.generator import (
    _clean_response,
    _build_context,
    _call_anthropic,
    _call_openai,
    generate_tests,
    DEFAULT_MODELS,
    _RETRY_DELAYS,
)
from src.prompts import SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_anthropic_client():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="generated playwright code")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_openai_client():
    mock_choice = MagicMock()
    mock_choice.message.content = "generated gherkin content"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 80
    mock_response.usage.completion_tokens = 40

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def minimal_analysis():
    return PageAnalysis(
        url="https://example.com",
        title="Example Domain",
        forms=[{"action": "/submit", "method": "POST", "fields": []}],
        interactive_elements=[{"tag": "button", "text": "Go", "role": "button"}],
        nav_links=[{"text": "Home", "href": "/"}],
        accessibility_tree="",
    )


@pytest.fixture
def error_analysis():
    return PageAnalysis(url="https://bad.example.com", title="Error: connection refused")


@pytest.fixture
def a11y_analysis():
    return PageAnalysis(
        url="https://example.com",
        title="Example Domain",
        forms=[],
        interactive_elements=[],
        nav_links=[],
        accessibility_tree='RootWebArea "Example Domain"\n  button "Submit"',
    )


# ---------------------------------------------------------------------------
# 2.2  _clean_response
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("```python\ncode here\n```", "code here"),
    ("```\ncode here\n```",       "code here"),
    ("import pytest\n\ndef test_foo(): pass", "import pytest\n\ndef test_foo(): pass"),
    ("\n\n  code  \n\n", "code"),
    ("```\nline1\nline2\nline3\n```", "line1\nline2\nline3"),
    ("```python\ncode", "code"),
])
def test_clean_response(text, expected):
    assert _clean_response(text, "playwright") == expected


# ---------------------------------------------------------------------------
# 2.3  _build_context
# ---------------------------------------------------------------------------

def test_build_context_valid_analysis_no_a11y(minimal_analysis):
    result = _build_context(analysis=minimal_analysis, include_a11y=False)
    assert "https://example.com" in result
    assert "Example Domain" in result
    assert "Accessibility tree" not in result


def test_build_context_valid_analysis_with_a11y(a11y_analysis):
    result = _build_context(analysis=a11y_analysis, include_a11y=True)
    assert "RootWebArea" in result


def test_build_context_a11y_flag_but_empty_tree(minimal_analysis):
    result = _build_context(analysis=minimal_analysis, include_a11y=True)
    assert "accessibility_tree" not in result
    assert "https://example.com" in result


def test_build_context_error_title_falls_back_to_url(error_analysis):
    result = _build_context(analysis=error_analysis, url="https://bad.example.com")
    assert result == "Generate test cases for the web page at: https://bad.example.com"


@pytest.mark.parametrize("kwargs,expected_fragment", [
    ({"url": "https://example.com"}, "https://example.com"),
    ({"description": "Login feature"}, "Login feature"),
])
def test_build_context_no_analysis_fallbacks(kwargs, expected_fragment):
    result = _build_context(analysis=None, **kwargs)
    assert expected_fragment in result


def test_build_context_neither_url_nor_description_raises():
    with pytest.raises(ValueError):
        _build_context(analysis=None, url=None, description=None)


def test_build_context_analysis_takes_priority_over_url(minimal_analysis):
    result = _build_context(analysis=minimal_analysis, url="https://other.com")
    assert "example.com" in result
    assert "other.com" not in result


# ---------------------------------------------------------------------------
# 2.4  _call_anthropic — happy path
# ---------------------------------------------------------------------------

def test_call_anthropic_returns_correct_tuple(mock_anthropic_client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
        patch("src.generator.console.print"),
    ):
        result = _call_anthropic("prompt", "test-model")
    assert result == ("generated playwright code", 100, 50)


def test_call_anthropic_passes_model_to_api(mock_anthropic_client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
        patch("src.generator.console.print"),
    ):
        _call_anthropic("prompt", "test-model")
    call_kwargs = mock_anthropic_client.messages.create.call_args
    assert call_kwargs.kwargs.get("model") == "test-model" or call_kwargs.args[0] == "test-model"


def test_call_anthropic_passes_system_prompt(mock_anthropic_client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
        patch("src.generator.console.print"),
    ):
        _call_anthropic("my prompt", "test-model")
    kwargs = mock_anthropic_client.messages.create.call_args.kwargs
    assert kwargs.get("system") == SYSTEM_PROMPT


def test_call_anthropic_passes_user_prompt(mock_anthropic_client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
        patch("src.generator.console.print"),
    ):
        _call_anthropic("my prompt", "test-model")
    kwargs = mock_anthropic_client.messages.create.call_args.kwargs
    assert kwargs.get("messages") == [{"role": "user", "content": "my prompt"}]


def test_call_anthropic_no_api_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        _call_anthropic("prompt", "model")


def test_call_anthropic_retry_true_default(mock_anthropic_client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
        patch("src.generator.console.print"),
    ):
        result = _call_anthropic("prompt", "test-model")
    assert result == ("generated playwright code", 100, 50)


def test_call_anthropic_retry_false(mock_anthropic_client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("anthropic.Anthropic", return_value=mock_anthropic_client),
        patch("src.generator.console.print"),
    ):
        result = _call_anthropic("prompt", "test-model", retry=False)
    assert result == ("generated playwright code", 100, 50)


# ---------------------------------------------------------------------------
# 2.4a  _call_anthropic — retry behaviour
# ---------------------------------------------------------------------------

class TestCallAnthropicRetry:
    """Retry behaviour for _call_anthropic."""

    def _good_response(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="generated playwright code")]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        return mock_response

    def test_call_anthropic_retries_on_failure(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        import anthropic as anthropic_module

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            anthropic_module.RateLimitError(
                message="rate limit",
                response=MagicMock(status_code=429, headers={}),
                body={},
            ),
            self._good_response(),
        ]

        with (
            patch("anthropic.Anthropic", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep"),
        ):
            result = _call_anthropic("prompt", "test-model")

        assert result == ("generated playwright code", 100, 50)
        assert mock_client.messages.create.call_count == 2

    def test_call_anthropic_raises_after_all_retries_exhausted(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        import anthropic as anthropic_module

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic_module.RateLimitError(
            message="always fails",
            response=MagicMock(status_code=429, headers={}),
            body={},
        )

        with (
            patch("anthropic.Anthropic", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep"),
        ):
            with pytest.raises(anthropic_module.RateLimitError):
                _call_anthropic("prompt", "test-model")

    def test_call_anthropic_no_retry_raises_immediately(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        import anthropic as anthropic_module

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic_module.RateLimitError(
            message="rate limit",
            response=MagicMock(status_code=429, headers={}),
            body={},
        )

        with (
            patch("anthropic.Anthropic", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep"),
        ):
            with pytest.raises(anthropic_module.RateLimitError):
                _call_anthropic("prompt", "test-model", retry=False)

        assert mock_client.messages.create.call_count == 1

    def test_call_anthropic_retry_sleeps_between_attempts(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        import anthropic as anthropic_module

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            anthropic_module.RateLimitError(
                message="fail 1",
                response=MagicMock(status_code=429, headers={}),
                body={},
            ),
            anthropic_module.RateLimitError(
                message="fail 2",
                response=MagicMock(status_code=429, headers={}),
                body={},
            ),
            self._good_response(),
        ]

        with (
            patch("anthropic.Anthropic", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep") as mock_sleep,
        ):
            _call_anthropic("prompt", "test-model")

        assert mock_sleep.called


# ---------------------------------------------------------------------------
# 2.5  _call_openai — happy path
# ---------------------------------------------------------------------------

def test_call_openai_returns_correct_tuple(mock_openai_client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("openai.OpenAI", return_value=mock_openai_client),
        patch("src.generator.console.print"),
    ):
        result = _call_openai("prompt", "test-model")
    assert result == ("generated gherkin content", 80, 40)


def test_call_openai_passes_model_to_api(mock_openai_client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("openai.OpenAI", return_value=mock_openai_client),
        patch("src.generator.console.print"),
    ):
        _call_openai("prompt", "test-model")
    kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
    assert kwargs.get("model") == "test-model"


def test_call_openai_passes_system_prompt(mock_openai_client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("openai.OpenAI", return_value=mock_openai_client),
        patch("src.generator.console.print"),
    ):
        _call_openai("my prompt", "test-model")
    kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
    messages = kwargs.get("messages", [])
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT


def test_call_openai_passes_user_prompt(mock_openai_client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("openai.OpenAI", return_value=mock_openai_client),
        patch("src.generator.console.print"),
    ):
        _call_openai("my prompt", "test-model")
    kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
    messages = kwargs.get("messages", [])
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "my prompt"


def test_call_openai_no_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        _call_openai("prompt", "model")


def test_call_openai_retry_true_default(mock_openai_client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("openai.OpenAI", return_value=mock_openai_client),
        patch("src.generator.console.print"),
    ):
        result = _call_openai("prompt", "test-model")
    assert result == ("generated gherkin content", 80, 40)


def test_call_openai_retry_false(mock_openai_client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("openai.OpenAI", return_value=mock_openai_client),
        patch("src.generator.console.print"),
    ):
        result = _call_openai("prompt", "test-model", retry=False)
    assert result == ("generated gherkin content", 80, 40)


# ---------------------------------------------------------------------------
# 2.5a  _call_openai — retry behaviour
# ---------------------------------------------------------------------------

class TestCallOpenAIRetry:
    """Retry behaviour for _call_openai."""

    def _good_response(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "generated gherkin content"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 80
        mock_response.usage.completion_tokens = 40
        return mock_response

    def _rate_limit_error(self):
        import openai as openai_module
        return openai_module.RateLimitError(
            message="rate limit",
            response=MagicMock(status_code=429, headers={}),
            body={},
        )

    def test_call_openai_retries_on_failure(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            self._rate_limit_error(),
            self._good_response(),
        ]

        with (
            patch("openai.OpenAI", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep"),
        ):
            result = _call_openai("prompt", "test-model")

        assert result == ("generated gherkin content", 80, 40)
        assert mock_client.chat.completions.create.call_count == 2

    def test_call_openai_raises_after_all_retries_exhausted(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import openai as openai_module

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = self._rate_limit_error()

        with (
            patch("openai.OpenAI", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep"),
        ):
            with pytest.raises(openai_module.RateLimitError):
                _call_openai("prompt", "test-model")

    def test_call_openai_no_retry_raises_immediately(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import openai as openai_module

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = self._rate_limit_error()

        with (
            patch("openai.OpenAI", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep"),
        ):
            with pytest.raises(openai_module.RateLimitError):
                _call_openai("prompt", "test-model", retry=False)

        assert mock_client.chat.completions.create.call_count == 1

    def test_call_openai_retry_sleeps_between_attempts(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            self._rate_limit_error(),
            self._rate_limit_error(),
            self._good_response(),
        ]

        with (
            patch("openai.OpenAI", return_value=mock_client),
            patch("src.generator.console.print"),
            patch("src.generator.time.sleep") as mock_sleep,
        ):
            _call_openai("prompt", "test-model")

        assert mock_sleep.called


# ---------------------------------------------------------------------------
# 2.6  generate_tests
# ---------------------------------------------------------------------------

_ANTHROPIC_RETURN = ("```python\nmy code\n```", 100, 50)
_OPENAI_RETURN = ("my gherkin", 80, 40)
_LOG_RETURN = {"estimated_cost_usd": 0.001}


@pytest.fixture
def gen_patches(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with (
        patch("src.generator._call_anthropic", return_value=_ANTHROPIC_RETURN) as mock_anth,
        patch("src.generator._call_openai", return_value=_OPENAI_RETURN) as mock_oai,
        patch("src.generator.log_api_call", return_value=_LOG_RETURN),
        patch("src.generator.console.print"),
    ):
        yield {"anthropic": mock_anth, "openai": mock_oai}


@pytest.mark.parametrize("fmt,provider,called,not_called", [
    ("playwright", "anthropic", "anthropic", "openai"),
    ("gherkin",    "anthropic", "anthropic", "openai"),
    ("playwright", "openai",    "openai",    "anthropic"),
    ("gherkin",    "openai",    "openai",    "anthropic"),
])
def test_generate_tests_provider_dispatch(fmt, provider, called, not_called, gen_patches):
    result = generate_tests(format=fmt, provider=provider, url="https://example.com")
    gen_patches[called].assert_called_once()
    gen_patches[not_called].assert_not_called()
    assert result  # non-empty


def test_generate_tests_default_model_anthropic(gen_patches):
    generate_tests(format="playwright", provider="anthropic", model=None, url="https://example.com")
    args, kwargs = gen_patches["anthropic"].call_args
    assert args[1] == DEFAULT_MODELS["anthropic"]


def test_generate_tests_default_model_openai(gen_patches):
    generate_tests(format="playwright", provider="openai", model=None, url="https://example.com")
    args, kwargs = gen_patches["openai"].call_args
    assert args[1] == DEFAULT_MODELS["openai"]


def test_generate_tests_custom_model(gen_patches):
    generate_tests(format="playwright", provider="anthropic", model="claude-haiku-custom", url="https://example.com")
    args, _ = gen_patches["anthropic"].call_args
    assert args[1] == "claude-haiku-custom"


def test_generate_tests_unknown_format_raises(gen_patches):
    with pytest.raises(ValueError, match="xml"):
        generate_tests(format="xml", provider="anthropic", url="https://example.com")


def test_generate_tests_unknown_provider_raises(gen_patches):
    with pytest.raises(ValueError, match="google"):
        generate_tests(format="playwright", provider="google", url="https://example.com")


def test_generate_tests_fences_stripped_in_output(gen_patches):
    result = generate_tests(format="playwright", provider="anthropic", url="https://example.com")
    assert not result.startswith("```")
    assert not result.endswith("```")


def test_generate_tests_log_api_call_invoked(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with (
        patch("src.generator._call_anthropic", return_value=_ANTHROPIC_RETURN),
        patch("src.generator._call_openai", return_value=_OPENAI_RETURN),
        patch("src.generator.log_api_call", return_value=_LOG_RETURN) as mock_log,
        patch("src.generator.console.print"),
    ):
        generate_tests(format="playwright", provider="anthropic", url="https://example.com")

    mock_log.assert_called_once()
    call_kwargs = mock_log.call_args.kwargs
    assert call_kwargs.get("provider") == "anthropic"
    assert call_kwargs.get("model") == DEFAULT_MODELS["anthropic"]
    assert "playwright" in call_kwargs.get("purpose", "")


def test_generate_tests_retry_true_passed_to_call(gen_patches):
    generate_tests(format="playwright", provider="anthropic", url="https://example.com", retry=True)
    _, kwargs = gen_patches["anthropic"].call_args
    assert kwargs.get("retry") is True


def test_generate_tests_retry_false_passed_to_call(gen_patches):
    generate_tests(format="playwright", provider="anthropic", url="https://example.com", retry=False)
    _, kwargs = gen_patches["anthropic"].call_args
    assert kwargs.get("retry") is False


def test_generate_tests_with_analysis_context(gen_patches, minimal_analysis):
    generate_tests(format="playwright", provider="anthropic", analysis=minimal_analysis, url=None, description=None)
    gen_patches["anthropic"].assert_called_once()


def test_generate_tests_with_description(gen_patches):
    generate_tests(format="playwright", provider="anthropic", description="Login page tests", url=None)
    gen_patches["anthropic"].assert_called_once()
