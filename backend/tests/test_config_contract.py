from pydantic import BaseSettings
from canvas.config import Settings


def test_settings_inherits_base_settings():
    """Test Settings class inherits from BaseSettings"""
    assert issubclass(Settings, BaseSettings)


def test_settings_has_database_url():
    """Test Settings has database_url field with str type"""
    field = Settings.__fields__['database_url']
    assert field.type_ == str


def test_settings_has_cors_origins():
    """Test Settings has cors_origins field with list[str] type"""
    field = Settings.__fields__['cors_origins']
    assert field.type_ == list[str]


def test_settings_has_log_level_default():
    """Test Settings has log_level field with INFO default"""
    field = Settings.__fields__['log_level']
    assert field.type_ == str
    assert field.default == "INFO"


def test_settings_has_secret_key():
    """Test Settings has secret_key field with str type"""
    field = Settings.__fields__['secret_key']
    assert field.type_ == str


def test_settings_env_prefix():
    """Test Settings Config.env_prefix is CANVAS_"""
    assert Settings.__config__.env_prefix == "CANVAS_"


def test_settings_case_insensitive():
    """Test Settings Config.case_sensitive is False"""
    assert Settings.__config__.case_sensitive is False