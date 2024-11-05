import os
import pytest
import yaml
from app.spotify_service.configuration.config_parser import ConfigParser


@pytest.fixture
def temp_spotify_config_file():
    """Fixture to create and remove a temporary YAML configuration file for testing."""
    
    path_to_config = "test_spotify_config.yaml"
    test_content = {
        "playlist": {
            "name": "My Playlist",
            "description": "A test playlist"
        },
        "api": {
            "version": "1.0",
            "authorization": {
                "auth_url": "https://example.com/auth",
                "redirect_url": "https://example.com/redirect",
                "permissions": "user-read-private",
                "token_url": "https://example.com/token",
                "user_auth_timemout_seconds": 30
            }
        }
    }

    with open(path_to_config, "w", encoding="UTF8") as file:
        yaml.dump(test_content, file, default_style='"')
    
    yield path_to_config

    if os.path.exists(path_to_config):
        os.remove(path_to_config)

def test_invalid_content(temp_spotify_config_file):
    with open(temp_spotify_config_file, "w", encoding="UTF8") as file:
        file.write("invalid_yaml_content")  # Write invalid content

    with pytest.raises(ValueError, match="The configuration file must contain a valid YAML dictionary structure."):
        ConfigParser(temp_spotify_config_file).parse()

def test_invalid_structure(temp_spotify_config_file):
    with open(temp_spotify_config_file, "w", encoding="UTF8") as file:
        file.write('"Just a string, not a dictionary."')  # Write invalid structure

    with pytest.raises(ValueError, match="The configuration file must contain a valid YAML dictionary structure."):
        ConfigParser(temp_spotify_config_file).parse()

def test_config_parsing(temp_spotify_config_file):
    config = ConfigParser(temp_spotify_config_file).parse()

    # Check for Playlist parsing
    assert config.playlist.name == "My Playlist"
    assert config.playlist.description == "A test playlist"

    # Check for API parsing
    assert config.api.version == "1.0"
    assert config.api.authorization.auth_url == "https://example.com/auth"
    assert config.api.authorization.redirect_url == "https://example.com/redirect"
    assert config.api.authorization.permissions == "user-read-private"
    assert config.api.authorization.token_url == "https://example.com/token"
    assert config.api.authorization.user_auth_timemout_seconds == 30
