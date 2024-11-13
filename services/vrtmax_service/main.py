import asyncio
import datetime

from vrtmax import get_logger, VRTMaxClient, VRTMaxClientError, VRTMaxClientConfig


logger = get_logger(__name__)

def setup_client() -> VRTMaxClient:
    vrtmax_client_config = VRTMaxClientConfig()
    vrtmax_client = VRTMaxClient(vrtmax_client_config)
    return vrtmax_client

async def main() -> None:
    client = setup_client()
    while True:
        try:
            new_tracks = client.ingest_new_tracks()

            logger.info("Simulating producer logic...")
            for track in new_tracks:
                logger.info("\t... Publishing track: %s by %s.", track.track_name, track.artist)

            await asyncio.sleep(datetime.timedelta(days=1).total_seconds())

        except VRTMaxClientError as e:
            logger.error("Unable to update the managed playlist: %s", str(e))


if __name__ == "__main__":
    asyncio.run(main())
