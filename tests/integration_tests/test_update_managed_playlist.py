import os
import pytest

from app.logging.logger import get_logger
from app.main import setup, update_managed_playlist
from app.spotify.environment.environment_types import EnvironmentTypes


logger = get_logger(__name__)

@pytest.fixture
def environment_type():
    """Determine the environment type based on an environment variable, defaulting to DEVELOPMENT."""
    
    env = os.getenv("ENV", "DEVELOPMENT").upper()
    logger.debug("Working environment retrieved: %s", env)

    try:
        return EnvironmentTypes[env]
    except KeyError as ke:
        raise ValueError(f"Invalid environment type: {env}. Must be one of {list(EnvironmentTypes)}.") from ke


@pytest.mark.filterwarnings("ignore::DeprecationWarning: httpx._content") # Ignore warning caused by the external package
@pytest.mark.asyncio
async def test_application_run(environment_type):
    """
    Test if the application can set up and run one update cycle without errors.
    This serves as a smoke test for the application's main workflow.
    """
    logger.critical("Testing application run in (%s) environment.", environment_type)
    # Perform the setup
    spotify_manager, vrtmax_client = await setup(environment_type)

    # Run one update cycle
    try:
        await update_managed_playlist(spotify_manager=spotify_manager, vrtmax_client=vrtmax_client)

    except Exception as e:
        pytest.fail(f"Application failed to run the update cycle without errors: {e}")
