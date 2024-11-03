import os
import pytest
from app.spotify.environment.environment import Environment

# Define constants used for environment variables in the tests
_SPOTIFY_CONFIG_FILE = "SPOTIFY_CONFIG_FILE"
_SPOTIFY_USER_ID = "SPOTIFY_USER_ID"
_SPOTIFY_PLAYLIST_ID = "SPOTIFY_PLAYLIST_ID"
_SPOTIFY_CLIENT_ID = "SPOTIFY_CLIENT_ID"
_SPOTIFY_CLIENT_SECRET = "SPOTIFY_CLIENT_SECRET"
_SPOTIFY_CLIENT_REFRESH_TOKEN = "SPOTIFY_CLIENT_REFRESH_TOKEN"
_SPOTIFY_TEMP_USER_AUTH_CODE = "TEMP_USER_AUTH_CODE"


@pytest.fixture
def env(mocker):
    """Fixture to create an Environment instance with dotenv loading mocked."""
    mocker.patch("app.spotify.environment.environment.load_dotenv", return_value=True)
    return Environment()


def test_spotify_client_id(env, mocker):
    """Test spotify_client_id property."""
    mocker.patch.dict(os.environ, {_SPOTIFY_CLIENT_ID: "test_client_id"})
    assert env.spotify_client_id == "test_client_id"


def test_spotify_user_id(env, mocker):
    """Test spotify_user_id property."""
    mocker.patch.dict(os.environ, {_SPOTIFY_USER_ID: "test_user_id"})
    assert env.spotify_user_id == "test_user_id"


def test_spotify_playlist_id(env, mocker):
    """Test spotify_playlist_id property."""
    mocker.patch.dict(os.environ, {_SPOTIFY_PLAYLIST_ID: "test_playlist_id"})
    assert env.spotify_playlist_id == "test_playlist_id"


def test_spotify_client_secret(env, mocker):
    """Test spotify_client_secret property."""
    mocker.patch.dict(os.environ, {_SPOTIFY_CLIENT_SECRET: "test_client_secret"})
    assert env.spotify_client_secret == "test_client_secret"


def test_spotify_client_refresh_token(env, mocker):
    """Test spotify_client_refresh_token property."""
    mocker.patch.dict(os.environ, {_SPOTIFY_CLIENT_REFRESH_TOKEN: "test_refresh_token"})
    assert env.spotify_client_refresh_token == "test_refresh_token"


def test_spotify_temp_user_auth_code(env, mocker):
    """Test spotify_temp_user_auth_code property."""
    mocker.patch.dict(os.environ, {_SPOTIFY_TEMP_USER_AUTH_CODE: "test_auth_code"})
    assert env.spotify_temp_user_auth_code == "test_auth_code"


def test_set_spotify_playlist_id(env, mocker):
    """Test spotify_playlist_id setter with a valid value."""
    mock_putenv = mocker.patch("app.spotify.environment.environment.os.putenv")
    mock_update_env_file = mocker.patch.object(env, "_Environment__update_env_file")

    env.spotify_playlist_id = "new_playlist_id"
    mock_putenv.assert_called_once_with(_SPOTIFY_PLAYLIST_ID, "new_playlist_id")
    mock_update_env_file.assert_called_once_with(_SPOTIFY_PLAYLIST_ID, "new_playlist_id")


def test_set_spotify_playlist_id_empty(env):
    """Test spotify_playlist_id setter with an empty value, expecting a ValueError."""
    with pytest.raises(ValueError):
        env.spotify_playlist_id = ""


def test_set_spotify_client_refresh_token(env, mocker):
    """Test spotify_client_refresh_token setter with a valid value."""
    mock_putenv = mocker.patch("app.spotify.environment.environment.os.putenv")
    mock_update_env_file = mocker.patch.object(env, "_Environment__update_env_file")

    env.spotify_client_refresh_token = "new_refresh_token"
    mock_putenv.assert_called_once_with(_SPOTIFY_CLIENT_REFRESH_TOKEN, "new_refresh_token")
    mock_update_env_file.assert_called_once_with(_SPOTIFY_CLIENT_REFRESH_TOKEN, "new_refresh_token")


def test_set_spotify_client_refresh_token_empty(env):
    """Test spotify_client_refresh_token setter with an empty value, expecting a ValueError."""
    with pytest.raises(ValueError):
        env.spotify_client_refresh_token = ""
