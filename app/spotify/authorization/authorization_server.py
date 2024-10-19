import asyncio
from typing import Optional
import uvicorn
from fastapi import Request

from app.logging.logger import get_logger


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

        @self.__config.app.get("/users/authorization/redirect")
        async def extract_code_and_state(request: Request) -> str:
            """Handles the OAuth redirect and extracts the authorization code and state."""
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            if not code:
                logger.error("Authorization code not provided in the redirect.")
                raise ValueError("Authorization code not provided in the redirect.")
            if self.__synchronization_state is None or state != self.__synchronization_state:
                logger.error("State mismatch: Response state does not match initial state. Rejecting authentication.")
                raise ValueError("Response state does not match initial state. Rejecting authentication attempt.")

            self.__auth_code = code
            logger.info("Authorization code received, signaling server to shut down.")
            self.__shutdown_event.set()  # Signal to shut down the server
            return "Authorization successful, this window may be closed."

    async def get_authorization_code(self, synchronization_state: str) -> str:
        """
        Starts the authorization server and waits for the authorization code.
        Returns this code once it's received and shuts down the server.
        """
        self.__synchronization_state = synchronization_state
        logger.debug("Synchronization state set: %s", synchronization_state)

        # Initialize the Uvicorn server with the configuration
        server = uvicorn.Server(self.__config)

        # Run the server in a separate asyncio task
        logger.info("Starting authorization server task in separate thread.")
        server_task = asyncio.create_task(self.__start_server(server))

        try:
            # Wait until the shutdown event is triggered (when the authorization code is received)
            logger.info("Waiting for authorization code and shutdown signal.")
            await self.__shutdown_event.wait()

            logger.info("Shutdown signal received. Attempting to shut down the server gracefully.")

            # Shutdown the server after receiving the shutdown signal
            await server.shutdown()

        except asyncio.CancelledError:
            logger.warning("Server shutdown process was interrupted or cancelled.")

        except Exception as e:
            logger.error("An error occurred while shutting down the server: %s", e)

        finally:
            if not server_task.done():
                logger.info("Cancelling the server task.")
                server_task.cancel()

                # Ensure the task is actually cancelled, and capture any exceptions raised during cancellation
                try:
                    await server_task
                except asyncio.CancelledError:
                    logger.info("Server task cancelled successfully.")

            # Clear the shutdown event for future use and ensure proper cleanup
            self.__shutdown_event.clear()
            logger.info("Authorization server shut down successfully.")

        # Return the authorization code after the server has been stopped
        return self.__auth_code

    async def __start_server(self, server: uvicorn.Server) -> None:
        try:
            logger.info("Starting up authorization redirect web server.")
            await server.serve()
        except Exception as e:
            logger.error("Error starting the authorization server: %s", str(e))
            raise RuntimeError("Failed to start the authorization server.") from e
