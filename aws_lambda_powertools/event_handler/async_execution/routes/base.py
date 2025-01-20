from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class BaseRoute(ABC):
    func: Callable

    @abstractmethod
    def match(self, event: dict[str, Any]) -> tuple[Callable, Any] | None:
        raise NotImplementedError()
