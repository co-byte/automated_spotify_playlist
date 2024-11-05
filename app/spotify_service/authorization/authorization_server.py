import asyncio
from typing import Optional
import uvicorn
from fastapi import Request

from app.spotify_service.logging.logger import get_logger


logger = get_logger(__name__)

class AuthorizationServer:
    def __init__(self, server_config: uvicorn.Config, user_authorization_timeout_seconds: int = 60):
        self.__config = server_config
        self.__user_auth_timeout = user_authorization_timeout_seconds
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
        Returns said code once received and shuts down the server.
        """
        self.__synchronization_state = synchronization_state
        server = uvicorn.Server(self.__config)

        try:
            server_task = asyncio.create_task(self.__start_server(server))
            await asyncio.wait_for(self.__shutdown_event.wait(), timeout=self.__user_auth_timeout)

            logger.info("Received shutdown signal and shutting down server.")
            return self.__auth_code

        except asyncio.TimeoutError as te:
            message = f"Authorization process timed out after waiting {self.__user_auth_timeout} seconds for user completion."
            logger.warning(message)
            raise TimeoutError(message) from te

        except asyncio.CancelledError as ce:
            logger.warning("Server shutdown process was cancelled.")
            raise ce

        except Exception as e:
            logger.error("Error retrieving authorization code: %s", e)
            raise RuntimeError(f"Failed to retrieve authorization code: {str(e)}") from e

        finally:
            await server.shutdown()
            await self.__cleanup_server_task(server_task)
