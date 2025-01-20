from __future__ import annotations

from typing import Any, Callable

from aws_lambda_powertools.utilities.data_classes.code_deploy_lifecycle_hook_event import (
    CodeDeployLifecycleHookEvent,
)

from .base import BaseRoute


class CodeDeployLifecycleHookRoute(BaseRoute):
    def __init__(self, func: Callable):
        self.func = func

    def match(self, event: dict[str, Any]) -> tuple[Callable, CodeDeployLifecycleHookEvent] | None:
        if not isinstance(event, dict):
            return None
        elif "DeploymentId" in event and "LifecycleEventHookExecutionId" in event:
            return self.func, CodeDeployLifecycleHookEvent(event)
        else:
            return None
