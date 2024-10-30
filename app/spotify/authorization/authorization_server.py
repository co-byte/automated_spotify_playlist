import asyncio
from typing import Optional
import uvicorn
from fastapi import Request

from app.logging.logger import get_logger


_AUTH_SERVER_TIMEOUT_SECONDS = 20

logger = get_logger(__name__)

class AuthorizationServer:
    def __init__(self, config: uvicorn.Config):
        self.__config = config
        self.__auth_code: Optional[str] = None
        self.__synchronization_state: Optional[str] = None
        self.__shutdown_event = asyncio.Event()
        self.__setup_routes()

    def __setup_routes(self) -> None:
        logger.debug("Setting up redirect endpoint.")
        self.__config.app.get("/users/authorization/redirect")(self.__extract_code_and_state)

    async def __start_server(self, server: uvicorn.Server) -> asyncio.Task:
        try:
            return asyncio.create_task(await server.serve())

        except Exception as e:
            logger.error("Error starting the authorization server: %s", str(e))
            raise RuntimeError("Failed to start the authorization server.") from e

    async def __extract_code_and_state(self, request: Request) -> str:
        """Handles the OAuth redirect and extracts the authorization code and state."""
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not code:
            message = "Authorization code not provided in the redirect."
            logger.error(message)
            raise ValueError(message)

        if self.__synchronization_state is None or state != self.__synchronization_state:
            message= "Response state does not match initial state. Rejecting authentication attempt."
            logger.error(message)
            raise ValueError(message)

        self.__auth_code = code
        logger.info("Authorization code received, signaling server to shut down.")
        self.__shutdown_event.set()  # Signal to shut down the server

        return "Authorization successful, this window may be closed."

    async def __cleanup_server_task(self, server_task: asyncio.Task) -> None:
        if not server_task.done():
            logger.debug("Cancelling the server task.")
            server_task.cancel()

            try:
                await server_task
            except asyncio.CancelledError:
                logger.debug("Server task cancelled successfully.")

        self.__shutdown_event.clear()
        logger.info("Authorization server shut down successfully.")

    async def get_authorization_code(self, synchronization_state: str) -> Optional[str]:
        """
        Starts the authorization server and waits for the authorization code.
        Returns this code once it's received and shuts down the server.
        """
        self.__synchronization_state = synchronization_state

        # Start the Uvicorn server on a separate thread
        server = uvicorn.Server(self.__config)
        server_task = asyncio.create_task(self.__start_server(server))

        try:
            logger.info("Starting authorization server task.")
            await asyncio.wait_for(
                self.__shutdown_event.wait(),
                timeout=_AUTH_SERVER_TIMEOUT_SECONDS
                )

            logger.info("Shutdown signal received. Attempting to shut down the server gracefully.")
            await server.shutdown()

            return self.__auth_code

        except asyncio.TimeoutError as te:
            logger.warning(
                "Server did not complete within %d seconds. Aborting the process.",
                _AUTH_SERVER_TIMEOUT_SECONDS
                )
            raise te

        except asyncio.CancelledError as ce:
            logger.warning("Server shutdown process was interrupted or cancelled.")
            raise ce

        finally:
            await server.shutdown()
            await self.__cleanup_server_task(server_task)
