from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .async_execution.exceptions import RouteNotFoundError
from .async_execution.router import Router

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext


class AsyncTriggerResolver(Router):
    current_event: Any
    lambda_context: LambdaContext | None
    raise_when_not_found: bool

    def __init__(self, raise_when_not_found: bool = True):
        super().__init__()
        self.current_event = None
        self.lambda_context = None
        self.raise_when_not_found = raise_when_not_found

    def resolve(self, event: dict[str, Any], context: LambdaContext):
        data = self.resolve_route(event=event)
        if data is None:
            if self.raise_when_not_found:
                raise RouteNotFoundError()
            else:
                return
        func, current_event = data
        try:
            self.current_event = current_event
            self.lambda_context = context
            return func()
        finally:
            self.current_event = None
            self.lambda_context = None
