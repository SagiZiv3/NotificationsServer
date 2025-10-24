import uvicorn
from fastapi import FastAPI

from dependency_injection import IDependencyContainer
from .endpoint_handler_builder import EndpointHandlerBuilder
from .models import Endpoint, Method, EndpointFunctionType


class WebApplication:
    def __init__(self, di_container: IDependencyContainer):
        self._di_container = di_container
        self._app = FastAPI(on_shutdown=[self._di_container.dispose])

    def map_get(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Get)

    def map_post(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Post)

    def map_put(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Put)

    def map_delete(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Delete)

    def map_patch(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Patch)

    def map_head(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Head)

    def map_options(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Options)

    def map_trace(self, route: str, function: EndpointFunctionType) -> EndpointHandlerBuilder:
        return self._map(route, function, Method.Trace)

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        uvicorn.run(self._app, host=host, port=port)

    def _map(self, route: str, function: EndpointFunctionType, method: Method) -> EndpointHandlerBuilder:
        endpoint = Endpoint(route, method, function)
        return EndpointHandlerBuilder(endpoint, self._di_container, self._di_container, self._register_endpoint)

    def _register_endpoint(self, endpoint: Endpoint) -> None:
        self._app.add_api_route(endpoint.route, endpoint.function, methods=[endpoint.method])
