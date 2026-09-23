# automated_spotify_playlist

[![Project Status: Inactive](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)

Keeps a Spotify playlist filled with the latest tracks from a VRT radio station (default: StuBru).

Every 24 hours the app pulls the last 100 tracks from the VRT MAX's GraphQL API, looks them up on
Spotify and swaps out the playlist's contents. If the playlist does not exist yet, a new one is created.

## Status

The project is not feature complete, but it works well enough for daily personal use. Active development has therefore stopped and maintenance will happen as time allows.

## Code structure

- `app/vrtmax/`: fetches the tracklist from VRT MAX
- `app/spotify/`: Oauth authentication, API requests and playlist logic
- `app/main.py`: wires everything together and makes it usable

## Setup

Requirements:

- Python 3.11
- A [Spotify developer app](https://developer.spotify.com/documentation/web-api/concepts/apps)
  with configured redirect URI (e.g. `http://localhost:5000/users/authorization/redirect` for local use)
  
```bash
pip install -r requirements.txt
```

### Configuration

Environment variables:

- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`: credentials of the Spotify app
- `SPOTIFY_USER_ID`: Spotify username
- `SPOTIFY_CONFIG_FILE`: path to the config file, usually `app/spotify/configuration/spotify_config.yaml`
- `SPOTIFY_CLIENT_REFRESH_TOKEN`: see [Authentication](#authentication)
- `SPOTIFY_PLAYLIST_ID`: existing playlist to update, leave empty to create a new one

Other settings:

- Playlist name, scopes and login timeout: `spotify_config.yaml`
- Radio station: `COMPONENT_ID` in `app/vrtmax/config/constants.py`
  (TODO: document how to find the ID of another station)

### Authentication

Without a refresh token, the app opens a browser to log in to Spotify and catches the redirect
(e.g. on `localhost:5000`), following the
[Authorization Code flow](https://developer.spotify.com/documentation/web-api/tutorials/code-flow).

## Running

### Development

Copy `app/spotify/environment/.env.template` to `.env` in the same folder, fill it in and run:

```bash
python -m app.main
```

The refresh token and playlist ID can be left empty since both will be written to `.env` after the first run.

### Production

```bash
python -m app.main --env production
```
Similar to development, but for persisted environments/secret stores (e.g. Running the code in a cloud environment).

## Tests

```bash
pytest tests/unit_tests
pytest tests/integration_tests   # real run, needs valid credentials
```

Unit tests run on every PR to `main` through GitHub Actions.

## License

GPL-3.0
