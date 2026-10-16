"""Environment overrides reach runtime calls without exposing credentials."""

import ast
import io
import json

import pytest

from config.settings import ROOT, CLIProxyConfig, DatabaseConfig, GroqConfig, load_environment
from config.testing import GenerationTestConfig
from rag.llm.groq_client import GroqClient
from rag.vectordb.postgres import connect


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    monkeypatch.setattr("config.settings.load_environment", lambda **_: None)
    monkeypatch.setattr("config.testing.load_environment", lambda **_: None)
    for name in (
        "GROQ_API_KEYS",
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "GROQ_FALLBACK_MODEL",
        "GROQ_MODERATION_MODEL",
        "GROQ_MAX_INPUT_CHARS",
        "GROQ_MAX_OUTPUT_TOKENS",
        "GROQ_MAX_CONTEXT_CHARS",
        "GROQ_REASONING_EFFORT",
        "GROQ_TIMEOUT_SECONDS",
        "GROQ_MAX_WAIT_SECONDS",
        "GROQ_TEMPERATURE",
        "CLIPROXYAPI_API_KEY",
        "CLIPROXYAPI_BASE_URL",
        "CLIPROXYAPI_MODEL",
        "CLIPROXYAPI_FALLBACK_MODEL",
        "CLIPROXYAPI_FALLBACK_REASONING_EFFORT",
        "CLIPROXYAPI_MAX_OUTPUT_TOKENS",
        "CLIPROXYAPI_REASONING_EFFORT",
        "CLIPROXYAPI_TIMEOUT_SECONDS",
        "CLIPROXYAPI_TEMPERATURE",
        "RAG_DB_PASSWORD",
        "RAG_DB_HOST",
        "RAG_DB_PORT",
        "RAG_DB_NAME",
        "RAG_DB_USER",
        "RAG_TEST_RUN_TESTS",
        "RAG_TEST_USE_RETRIEVAL_CACHE",
        "RAG_TEST_MIN_TURN_INTERVAL_SECONDS",
        "RAG_TEST_CASE_IDS",
        "RAG_TEST_RUN_CUSTOM_CASE",
    ):
        monkeypatch.delenv(name, raising=False)


def test_env_settings_reach_model_payload_timeout_and_key_rotation(monkeypatch):
    values = {
        "GROQ_API_KEYS": "fixture-one,fixture-two,fixture-one",
        "GROQ_MODEL": "qwen/fixture-primary",
        "GROQ_FALLBACK_MODEL": "fixture-fallback",
        "GROQ_MODERATION_MODEL": "fixture-moderation",
        "GROQ_MAX_INPUT_CHARS": "9000",
        "GROQ_MAX_OUTPUT_TOKENS": "1234",
        "GROQ_MAX_CONTEXT_CHARS": "7000",
        "GROQ_REASONING_EFFORT": "low",
        "GROQ_TIMEOUT_SECONDS": "1.25",
        "GROQ_MAX_WAIT_SECONDS": "0.5",
        "GROQ_TEMPERATURE": "0.4",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    settings = GroqConfig.from_env()
    assert settings.keys == ("fixture-one", "fixture-two")
    assert settings.fallback_model == "fixture-fallback"
    assert settings.moderation_model == "fixture-moderation"
    assert (settings.max_input_chars, settings.max_context_chars) == (9000, 7000)
    assert settings.max_wait_seconds == 0.5
    assert "fixture-one" not in repr(settings)
    calls = []

    def send(request, **kwargs):
        payload = json.loads(request.data)
        assert payload["model"] == "qwen/fixture-primary"
        assert payload["max_completion_tokens"] == 1234
        assert payload["reasoning_effort"] == "low"
        assert payload["temperature"] == 0.4
        assert kwargs["timeout"] == 1.25
        calls.append(request.get_header("Authorization"))
        return io.BytesIO(
            json.dumps(
                {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}
            ).encode()
        )

    monkeypatch.setattr("rag.llm.groq_client.urlopen", send)
    client = GroqClient()
    client.complete([], {})
    client.complete([], {})
    assert calls == ["Bearer fixture-one", "Bearer fixture-two"]


def test_dotenv_precedence_and_explicit_notebook_reload(monkeypatch, tmp_path):
    monkeypatch.setattr("config.settings.ROOT", tmp_path)
    (tmp_path / ".env").write_text(
        "GROQ_MODEL=fixture-file-model\nGROQ_API_KEYS=fixture-file-key\n"
    )
    monkeypatch.setenv("GROQ_MODEL", "fixture-process-model")
    load_environment()
    assert GroqConfig.from_env().model == "fixture-process-model"
    load_environment(override=True)
    assert GroqConfig.from_env().model == "fixture-file-model"


@pytest.mark.parametrize(
    "name,value",
    [
        ("GROQ_TIMEOUT_SECONDS", "0"),
        ("GROQ_TIMEOUT_SECONDS", "nan"),
        ("GROQ_MAX_WAIT_SECONDS", "-1"),
        ("GROQ_MAX_WAIT_SECONDS", "inf"),
        ("GROQ_TEMPERATURE", "3"),
        ("GROQ_MAX_CONTEXT_CHARS", "0"),
        ("GROQ_REASONING_EFFORT", "invalid"),
        ("GROQ_MODEL", ""),
    ],
)
def test_invalid_env_is_rejected_before_network_calls(monkeypatch, name, value):
    monkeypatch.setenv("GROQ_API_KEYS", "fixture-one")
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        GroqClient()


def test_cliproxy_settings_read_local_client_key_and_allow_env_override(monkeypatch, tmp_path):
    monkeypatch.setattr("config.settings.ROOT", tmp_path)
    directory = tmp_path / "config/cliproxyapi/local"
    directory.mkdir(parents=True)
    (directory / "credentials.env").write_text(
        "MANAGEMENT_PASSWORD=admin-only\nCLIPROXYAPI_CLIENT_API_KEY=local-client\n"
    )
    config = CLIProxyConfig.from_env()
    assert config.api_key == "local-client"
    assert config.model == "gemini-3.5-flash-lite"
    assert config.fallback_model == "gpt-oss-120b-medium"
    assert config.fallback_reasoning_effort == "medium"
    assert "local-client" not in repr(config) and "admin-only" not in repr(config)
    monkeypatch.setenv("CLIPROXYAPI_API_KEY", "env-client")
    monkeypatch.setenv("CLIPROXYAPI_BASE_URL", "http://cliproxyapi:8317/v1/")
    assert CLIProxyConfig.from_env().api_key == "env-client"
    assert CLIProxyConfig.from_env().base_url == "http://cliproxyapi:8317/v1"


@pytest.mark.parametrize(
    "name,value",
    [
        ("CLIPROXYAPI_API_KEY", ""),
        ("CLIPROXYAPI_BASE_URL", "file:///tmp/secret"),
        ("CLIPROXYAPI_BASE_URL", "http://key@localhost/v1"),
        ("CLIPROXYAPI_MODEL", ""),
        ("CLIPROXYAPI_FALLBACK_MODEL", ""),
        ("CLIPROXYAPI_FALLBACK_MODEL", "gemini-3.5-flash-lite"),
        ("CLIPROXYAPI_FALLBACK_REASONING_EFFORT", "invalid"),
        ("CLIPROXYAPI_MAX_OUTPUT_TOKENS", "0"),
        ("CLIPROXYAPI_TIMEOUT_SECONDS", "nan"),
        ("CLIPROXYAPI_TIMEOUT_SECONDS", "0"),
        ("CLIPROXYAPI_TEMPERATURE", "inf"),
        ("CLIPROXYAPI_REASONING_EFFORT", "invalid"),
    ],
)
def test_invalid_cliproxy_settings_are_rejected(monkeypatch, name, value):
    monkeypatch.setenv("CLIPROXYAPI_API_KEY", "fixture-client")
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        CLIProxyConfig.from_env()


@pytest.mark.parametrize(
    "preset,model,effort,fallback,fallback_effort",
    [
        ("3.5-lite-high", "gemini-3.5-flash-lite", "high", "gpt-oss-120b-medium", "medium"),
        ("3.8-high", "gemini-3.8-flash-high", "high", "gpt-oss-120b-medium", "medium"),
        ("120b", "gpt-oss-120b-medium", "medium", "gemini-3.5-flash-lite", "high"),
    ],
)
def test_model_presets_override_old_model_env_without_changing_connection_settings(
    monkeypatch, preset, model, effort, fallback, fallback_effort
):
    monkeypatch.setenv("CLIPROXYAPI_API_KEY", "fixture-client")
    monkeypatch.setenv("CLIPROXYAPI_MODEL", "gemini-3.8-flash-high")
    monkeypatch.setenv("CLIPROXYAPI_REASONING_EFFORT", "low")
    monkeypatch.setenv("CLIPROXYAPI_FALLBACK_MODEL", "gpt-oss-120b-medium")
    monkeypatch.setenv("CLIPROXYAPI_FALLBACK_REASONING_EFFORT", "low")
    monkeypatch.setenv("CLIPROXYAPI_BASE_URL", "http://fixture-gateway:8317/v1")
    monkeypatch.setenv("CLIPROXYAPI_MAX_OUTPUT_TOKENS", "4096")
    config = CLIProxyConfig.from_env(model_preset=preset)
    assert (config.model, config.reasoning_effort) == (model, effort)
    assert (config.fallback_model, config.fallback_reasoning_effort) == (fallback, fallback_effort)
    assert config.api_key == "fixture-client"
    assert config.base_url == "http://fixture-gateway:8317/v1"
    assert config.max_output_tokens == 4096


def test_120b_selection_resolves_same_model_env_before_config_validation(monkeypatch):
    monkeypatch.setenv("CLIPROXYAPI_API_KEY", "fixture-client")
    monkeypatch.setenv("CLIPROXYAPI_MODEL", "gpt-oss-120b-medium")
    monkeypatch.setenv("CLIPROXYAPI_FALLBACK_MODEL", "gpt-oss-120b-medium")
    config = CLIProxyConfig.from_env(model_preset="120b")
    assert config.model == "gpt-oss-120b-medium"
    assert config.fallback_model == "gemini-3.5-flash-lite"
    with pytest.raises(ValueError):
        CLIProxyConfig.from_env()


@pytest.mark.parametrize("name", ["GROQ_MAX_OUTPUT_TOKENS", "CLIPROXYAPI_MAX_OUTPUT_TOKENS"])
def test_model_output_setting_uses_full_model_limit_instead_of_a_fixed_default(monkeypatch, name):
    monkeypatch.setenv("GROQ_API_KEYS", "fixture-groq")
    monkeypatch.setenv("CLIPROXYAPI_API_KEY", "fixture-cli")
    monkeypatch.setenv(name, "model")
    config = GroqConfig.from_env() if name.startswith("GROQ_") else CLIProxyConfig.from_env()
    assert config.max_output_tokens is None


def test_database_connection_uses_env_and_hides_password(monkeypatch):
    for name, value in {
        "RAG_DB_PASSWORD": "fixture-password",
        "RAG_DB_HOST": "fixture-host",
        "RAG_DB_PORT": "55499",
        "RAG_DB_NAME": "fixture-db",
        "RAG_DB_USER": "fixture-user",
    }.items():
        monkeypatch.setenv(name, value)
    assert "fixture-password" not in repr(DatabaseConfig.from_env())
    calls = []
    connection = object()

    def open_connection(**kwargs):
        calls.append(kwargs)
        return connection

    monkeypatch.setattr("rag.vectordb.postgres.psycopg.connect", open_connection)
    monkeypatch.setattr("rag.vectordb.postgres.register_vector", lambda _: None)
    assert connect() is connection
    for name, expected in {
        "host": "fixture-host",
        "port": 55499,
        "dbname": "fixture-db",
        "user": "fixture-user",
        "password": "fixture-password",
    }.items():
        assert calls[0][name] == expected


def test_notebook_controls_are_loaded_from_env(monkeypatch):
    monkeypatch.setenv("RAG_TEST_RUN_TESTS", "false")
    monkeypatch.setenv("RAG_TEST_USE_RETRIEVAL_CACHE", "0")
    monkeypatch.setenv("RAG_TEST_MIN_TURN_INTERVAL_SECONDS", "12.5")
    monkeypatch.setenv("RAG_TEST_CASE_IDS", "hs_missing_material, qa_missing_context")
    monkeypatch.setenv("RAG_TEST_RUN_CUSTOM_CASE", "true")
    settings = GenerationTestConfig.from_env()
    assert not settings.run_tests and not settings.use_retrieval_cache
    assert settings.run_custom_case
    assert settings.min_turn_interval_seconds == 12.5
    assert settings.case_ids == ("hs_missing_material", "qa_missing_context")


def test_rag_runtime_never_imports_test_runners():
    for path in (ROOT / "rag").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(("tests", "pytest", "unittest")), path
            elif isinstance(node, ast.Import):
                assert not any(
                    a.name.startswith(("tests", "pytest", "unittest")) for a in node.names
                ), path
