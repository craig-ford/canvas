from pydantic_settings import BaseSettings
from canvas.config import Settings


def test_settings_inherits_base_settings():
    """Test Settings class inherits from BaseSettings"""
    assert issubclass(Settings, BaseSettings)


def test_settings_has_database_url():
    """Test Settings has database_url field with str type"""
    field_info = Settings.model_fields['database_url']
    assert field_info.annotation is str


def test_settings_has_cors_origins():
    """Test Settings has cors_origins field with list[str] type"""
    field_info = Settings.model_fields['cors_origins']
    assert field_info.annotation == list[str]


def test_settings_has_log_level_default():
    """Test Settings has log_level field with INFO default"""
    field_info = Settings.model_fields['log_level']
    assert field_info.annotation is str
    assert field_info.default == "INFO"


def test_settings_has_secret_key():
    """Test Settings has secret_key field with str type"""
    field_info = Settings.model_fields['secret_key']
    assert field_info.annotation is str


def test_settings_env_prefix():
    """Test Settings env_prefix is CANVAS_"""
    assert Settings.model_config.get('env_prefix') == "CANVAS_"


def test_settings_case_insensitive():
    """Test Settings case_sensitive is False"""
    assert Settings.model_config.get('case_sensitive') is False
