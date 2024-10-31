import pytest
from app.main import setup, update_managed_playlist

@pytest.mark.asyncio
async def test_application_run():
    """
    Test if the application can set up and run one update cycle without errors.
    This serves as a smoke test for the application's main workflow.
    """
    # Perform the setup
    spotify_manager, vrtmax_client = await setup()

    # Run one update cycle
    try:
        await update_managed_playlist(spotify_manager=spotify_manager, vrtmax_client=vrtmax_client)

    except Exception as e:
        pytest.fail(f"Application failed to run the update cycle without errors: {e}")
