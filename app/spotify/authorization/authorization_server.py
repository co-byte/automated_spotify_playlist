import asyncio
from fastapi import Request
import uvicorn


class AuthorizationServer:
    def __init__(self, config: uvicorn.Config):
        self.__config = config
        self.__shutdown_event = asyncio.Event()
        self.__auth_code: str = None
        self.__synchronization_state: str = None
        self.__setup_routes()

    def __setup_routes(self) -> None:
        @self.__config.app.get("/users/authorization/redirect")
        async def extract_code_and_state(request: Request) -> str:
            """Handles the OAuth redirect and extracts the authorization code and state."""
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            if not code:
                raise ValueError("Error: code was not provided.")
            if self.__synchronization_state is None or state != self.__synchronization_state:
                raise ValueError("Response state does not match initial state. Rejecting authentication attempt.")

            self.__auth_code = code
            print("authorization_manager - Auth code received, signalling server to shut down.")
            self.__shutdown_event.set()  # Signal to shut down the server
            return "Authorization successful, this window may be closed."

    async def get_authorization_code(self, synchronization_state: str) -> str:
        """
        Starts the authorization server and waits for the authorization code.
        Returns this code once it's received and shuts down the server.
        """
        self.__synchronization_state = synchronization_state
        server = uvicorn.Server(self.__config)

        # Run the server in a separate asyncio task
        print("authorization_manager - Starting up auth server.")
        server_task = asyncio.create_task(server.serve())

        # Wait for the shutdown event to be set (when the authorization code is received)
        await self.__shutdown_event.wait()

        # Shutdown the server, ensure the server task finishes and clear the shutdown flag
        await server.shutdown()
        server_task.cancel()
        self.__shutdown_event.clear()

        print("authorization_manager - Auth server successfully shut down.")
        return self.__auth_code
