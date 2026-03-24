from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Annotated

from annotated_doc import Doc


ASGIApp = Annotated[
    Callable[[dict, Callable, Callable], Awaitable[None]],
    Doc("ASGI application callable that handles requests")
]


class BaseMiddleware(ABC):
    """Base class for all middleware."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application to wrap")
    ], config: Annotated[
        "dict | None",
        Doc("Middleware configuration dictionary")
    ] = None):
        self.app = app
        self.config = config or {}

    @abstractmethod
    async def __call__(self, scope: Annotated[
        dict,
        Doc("ASGI scope dictionary")
    ], receive: Annotated[
        Callable,
        Doc("ASGI receive callable")
    ], send: Annotated[
        Callable,
        Doc("ASGI send callable")
    ]) -> None:
        """Process the request through middleware."""
        pass


class MiddlewareChain:
    """Chain of middleware processors."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application")
    ], middlewares: Annotated[
        list[BaseMiddleware],
        Doc("List of middleware to apply in order")
    ]):
        self.app = app
        self.middlewares = middlewares

    def build(self) -> Annotated[
        ASGIApp,
        Doc("ASGI application with middleware chain applied")
    ]:
        """Build the middleware chain."""
        if not self.middlewares:
            return self.app
        reversed_middlewares = list(reversed(self.middlewares))
        current_app = self.app
        for middleware in reversed_middlewares:
            current_app = self._wrap(middleware, current_app)
        return current_app

    def _wrap(self, middleware: Annotated[
        BaseMiddleware,
        Doc("Middleware to wrap")
    ], next_app: Annotated[
        ASGIApp,
        Doc("Next ASGI application in chain")
    ]) -> Annotated[
        ASGIApp,
        Doc("Wrapped ASGI application")
    ]:
        """Wrap middleware around the app."""
        async def wrapped(scope: dict, receive: Callable, send: Callable) -> None:
            original_app = middleware.app
            middleware.app = next_app
            try:
                await middleware(scope, receive, send)
            finally:
                middleware.app = original_app
        return wrapped
