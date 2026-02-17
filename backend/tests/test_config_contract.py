from pydantic_settings import BaseSettings
from canvas.config import Settings


def test_settings_inherits_base_settings():
    """Test Settings class inherits from BaseSettings"""
    assert issubclass(Settings, BaseSettings)


def test_settings_has_database_url():
    """Test Settings has database_url field with str type"""
    field_info = Settings.model_fields['database_url']
    assert field_info.annotation is str
    # Check it's required (PydanticUndefined means no default)
    from pydantic_core import PydanticUndefined
    assert field_info.default is PydanticUndefined


def test_settings_has_cors_origins():
    """Test Settings has cors_origins field with list[str] type"""
    field_info = Settings.model_fields['cors_origins']
    assert field_info.annotation == list[str]
    # Check it's required (PydanticUndefined means no default)
    from pydantic_core import PydanticUndefined
    assert field_info.default is PydanticUndefined


def test_settings_has_log_level_default():
    """Test Settings has log_level field with INFO default"""
    field_info = Settings.model_fields['log_level']
    assert field_info.annotation is str
    assert field_info.default == "INFO"


def test_settings_has_secret_key():
    """Test Settings has secret_key field with str type"""
    field_info = Settings.model_fields['secret_key']
    assert field_info.annotation is str
    # Check it's required (PydanticUndefined means no default)
    from pydantic_core import PydanticUndefined
    assert field_info.default is PydanticUndefined


def test_settings_env_prefix():
    """Test Settings env_prefix is CANVAS_"""
    assert Settings.model_config.get('env_prefix') == "CANVAS_"


def test_settings_case_insensitive():
    """Test Settings case_sensitive is False"""
    assert Settings.model_config.get('case_sensitive') is False


def test_settings_has_token_expiry_defaults():
    """Test Settings has token expiry fields with correct defaults"""
    access_field = Settings.model_fields['access_token_expire_minutes']
    refresh_field = Settings.model_fields['refresh_token_expire_days']
    assert access_field.annotation is int
    assert refresh_field.annotation is int
    assert access_field.default == 30
    assert refresh_field.default == 7


def test_settings_has_upload_config():
    """Test Settings has upload configuration with defaults"""
    upload_dir_field = Settings.model_fields['upload_dir']
    max_size_field = Settings.model_fields['max_upload_size_mb']
    assert upload_dir_field.annotation is str
    assert max_size_field.annotation is int
    assert upload_dir_field.default == "/uploads"
    assert max_size_field.default == 10
