import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, Union

from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger(__name__)


class RouterContext:
    def __init__(self):
        self._context = {}

    @property
    def context(self) -> Dict[str, Any]:
        return self._context

    @context.setter
    def context(self, additional_context: Dict[str, Any]) -> None:
        """Append key=value data as routing context"""
        self._context.update(**additional_context)

    @context.deleter
    def context(self):
        """Resets routing context"""
        self._context.clear()


class BaseResolverRegistry(ABC):
    @property
    @abstractmethod
    def resolvers(self) -> Dict[str, Dict[str, Any]]:
        ...

    @resolvers.setter
    @abstractmethod
    def resolvers(self, resolvers: dict) -> None:
        ...

    @abstractmethod
    def resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        ...

    @abstractmethod
    def find_resolver(self, type_name: str, field_name: str) -> Optional[Callable]:
        ...


class BasePublic(ABC):
    @abstractmethod
    def resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        ...

    @abstractmethod
    def batch_resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        ...

    @abstractmethod
    def append_context(self, **additional_context) -> None:
        ...


class ResolverRegistry(BaseResolverRegistry):
    def __init__(self):
        self._resolvers: Dict[str, Dict[str, Any]] = {}

    @property
    def resolvers(self) -> Dict[str, Dict[str, Any]]:
        return self._resolvers

    @resolvers.setter
    def resolvers(self, resolvers: dict) -> None:
        self._resolvers.update(resolvers)

    def resolver(self, type_name: str = "*", field_name: Optional[str] = None):
        """Registers the resolver for field_name

        Parameters
        ----------
        type_name : str
            Type name
        field_name : str
            Field name
        """

        def register(func):
            logger.debug(f"Adding resolver `{func.__name__}` for field `{type_name}.{field_name}`")
            self._resolvers[f"{type_name}.{field_name}"] = {"func": func}
            return func

        return register

    def find_resolver(self, type_name: str, field_name: str) -> Optional[Callable]:
        """Find resolver based on type_name and field_name

        Parameters
        ----------
        type_name : str
            Type name
        field_name : str
            Field name
        """

        resolver = self._resolvers.get(f"{type_name}.{field_name}", self._resolvers.get(f"*.{field_name}"))
        if not resolver:
            return None
        return resolver["func"]


class Router(BasePublic):
    def __init__(self):
        self._resolver_registry: BaseResolverRegistry = ResolverRegistry()
        self._batch_resolver_registry: BaseResolverRegistry = ResolverRegistry()
        self._batch_async_resolver_registry: BaseResolverRegistry = ResolverRegistry()
        self._router_context: RouterContext = RouterContext()

    # Interfaces
    def resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        return self._resolver_registry.resolver(field_name=field_name, type_name=type_name)

    def batch_resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        return self._batch_resolver_registry.resolver(field_name=field_name, type_name=type_name)

    def batch_async_resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        return self._batch_async_resolver_registry.resolver(field_name=field_name, type_name=type_name)

    def append_context(self, **additional_context) -> None:
        self._router_context.context = additional_context


class AppSyncResolver(Router):
    """
    AppSync resolver decorator

    Example
    -------

    **Sample usage**

        from aws_lambda_powertools.event_handler import AppSyncResolver

        app = AppSyncResolver()

        @app.resolver(type_name="Query", field_name="listLocations")
        def list_locations(page: int = 0, size: int = 10) -> list:
            # Your logic to fetch locations with arguments passed in
            return [{"id": 100, "name": "Smooth Grooves"}]

        @app.resolver(type_name="Merchant", field_name="extraInfo")
        def get_extra_info() -> dict:
            # Can use "app.current_event.source" to filter within the parent context
            account_type = app.current_event.source["accountType"]
            method = "BTC" if account_type == "NEW" else "USD"
            return {"preferredPaymentMethod": method}

        @app.resolver(field_name="commonField")
        def common_field() -> str:
            # Would match all fieldNames matching 'commonField'
            return str(uuid.uuid4())
    """

    def __init__(self):
        super().__init__()
        self.current_batch_event: List[AppSyncResolverEvent] = []
        self.current_event: Optional[AppSyncResolverEvent] = None
        self.lambda_context: Optional[LambdaContext] = None

    def resolve(
        self,
        event: Union[dict, List[Dict]],
        context: LambdaContext,
        data_model: Type[AppSyncResolverEvent] = AppSyncResolverEvent,
    ) -> Any:
        """Resolve field_name in single event or in a batch event

        Parameters
        ----------
        event : dict | List[Dict]
            Lambda event either coming from batch processing endpoint or from standard processing endpoint
        context : LambdaContext
            Lambda context
        data_model:
            Your data data_model to decode AppSync event, by default AppSyncResolverEvent

        Example
        -------

        ```python
        from aws_lambda_powertools.event_handler import AppSyncResolver
        from aws_lambda_powertools.utilities.typing import LambdaContext

        @app.resolver(field_name="createSomething")
        def create_something(id: str):  # noqa AA03 VNE003
            return id

        def handler(event, context: LambdaContext):
            return app.resolve(event, context)
        ```

        **Bringing custom models**

        ```python
        from aws_lambda_powertools import Logger, Tracer

        from aws_lambda_powertools.logging import correlation_paths
        from aws_lambda_powertools.event_handler import AppSyncResolver

        tracer = Tracer(service="sample_resolver")
        logger = Logger(service="sample_resolver")
        app = AppSyncResolver()


        class MyCustomModel(AppSyncResolverEvent):
            @property
            def country_viewer(self) -> str:
                return self.request_headers.get("cloudfront-viewer-country")


        @app.resolver(field_name="listLocations")
        @app.resolver(field_name="locations")
        def get_locations(name: str, description: str = ""):
            if app.current_event.country_viewer == "US":
                ...
            return name + description


        @logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER)
        @tracer.capture_lambda_handler
        def lambda_handler(event, context):
            return app.resolve(event, context, data_model=MyCustomModel)
        ```

        Returns
        -------
        Any
            Returns the result of the resolver

        Raises
        -------
        ValueError
            If we could not find a field resolver
        """

        self.lambda_context = context

        response = (
            self._call_batch_resolver(event=event, data_model=data_model)
            if isinstance(event, list)
            else self._call_single_resolver(event=event, data_model=data_model)
        )
        del self._router_context.context

        return response

    def _call_single_resolver(self, event: dict, data_model: Type[AppSyncResolverEvent]) -> Any:
        """Call single event resolver

        Parameters
        ----------
        event : dict
            Event
        data_model : Type[AppSyncResolverEvent]
            Data_model to decode AppSync event, by default it is of AppSyncResolverEvent type or subclass of it
        """

        self.current_event = data_model(event)
        resolver = self._resolver_registry.find_resolver(self.current_event.type_name, self.current_event.field_name)
        if not resolver:
            raise ValueError(f"No resolver found for '{self.current_event.type_name}.{self.current_event.field_name}'")
        return resolver(**self.current_event.arguments)

    def _call_sync_batch_resolver(self, sync_resolver: Callable) -> List[Any]:
        return [
            sync_resolver(event=appconfig_event, **appconfig_event.arguments)
            for appconfig_event in self.current_batch_event
        ]

    async def _call_async_batch_resolver(self, async_resolver: Callable) -> List[Any]:
        tasks = [
            asyncio.ensure_future(async_resolver(event=appconfig_event, **appconfig_event.arguments))
            for appconfig_event in self.current_batch_event
        ]
        return await asyncio.gather(*tasks)

    def _call_batch_resolver(self, event: List[dict], data_model: Type[AppSyncResolverEvent]) -> List[Any]:
        """Call batch event resolver for sync and async methods

        Parameters
        ----------
        event : List[dict]
            Event
        data_model : Type[AppSyncResolverEvent]
            Data_model to decode AppSync event, by default it is of AppSyncResolverEvent type or subclass of it
        """

        # Check if all events have the same field name
        if len({x["info"]["fieldName"] for x in event}) > 1:
            ValueError("batch with different field names. It shouldn't happen!")

        self.current_batch_event = [data_model(e) for e in event]

        # Check if we have synchronous or asynchronous resolver available
        resolver = self._batch_resolver_registry.find_resolver(
            self.current_batch_event[0].type_name,
            self.current_batch_event[0].field_name,
        )
        async_resolver = self._batch_async_resolver_registry.find_resolver(
            self.current_batch_event[0].type_name,
            self.current_batch_event[0].field_name,
        )
        if resolver:
            return self._call_sync_batch_resolver(resolver)
        elif async_resolver:
            return asyncio.run(self._call_async_batch_resolver(async_resolver))
        else:
            raise ValueError(
                f"No resolver found for \
                    '{self.current_batch_event[0].type_name}.{self.current_batch_event[0].field_name}'",
            )

    def __call__(
        self,
        event: dict,
        context: LambdaContext,
        data_model: Type[AppSyncResolverEvent] = AppSyncResolverEvent,
    ) -> Any:
        """Implicit lambda handler which internally calls `resolve`"""
        return self.resolve(event, context, data_model)

    def include_router(self, router: "Router") -> None:
        """Adds all resolvers defined in a router

        Parameters
        ----------
        router : Router
            A router containing a dict of field resolvers
        """

        # Merge app and router context
        self._router_context.context = router._router_context.context
        # use pointer to allow context clearance after event is processed e.g., resolve(evt, ctx)
        router._router_context._context = self._router_context.context

        self._resolver_registry.resolvers = router._resolver_registry.resolvers
        self._batch_resolver_registry.resolvers = router._batch_resolver_registry.resolvers
        self._batch_async_resolver_registry.resolvers = router._batch_async_resolver_registry.resolvers

    # Interfaces
    def resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        return self._resolver_registry.resolver(field_name=field_name, type_name=type_name)

    def batch_resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        return self._batch_resolver_registry.resolver(field_name=field_name, type_name=type_name)

    def batch_async_resolver(self, type_name: str = "*", field_name: Optional[str] = None) -> Callable:
        return self._batch_async_resolver_registry.resolver(field_name=field_name, type_name=type_name)

    def append_context(self, **additional_context) -> None:
        self._router_context.context = additional_context
