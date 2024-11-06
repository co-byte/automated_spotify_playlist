import asyncio
import datetime

from services.vrtmax_service.logging.logger import get_logger
from services.vrtmax_service.config.vrtmax_client_config import VRTMaxClientConfig
from services.vrtmax_service.vrtmax.vrtmax_client import VRTMaxClient, VRTMaxClientError


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
