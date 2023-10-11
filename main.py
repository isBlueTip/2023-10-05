# вынести валидацию из контроллеров
# вынести повторяющийся код
# больше разделить код каждого контроллера по назначению
# Возможно, нужен ещё один слой доступа к БД
# Не хватило времени разобраться с запуском в контейнере
# Приложение в контейнере не видит БД

import asyncio
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import ipdb

import exceptions
from controllers import ResourceController, ResourceTypeController
from views import ResourceSerializer, ResourceTypeSerializer

URL_SCHEME = "scheme://path;parameters?query"


# server that sends all the request info to a specific controller
class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        """
        Init additional parameters.
        :param args:
        :param kwargs:
        """

        self.parsed_url = None
        self.url_params: dict = {}
        self.request_json: dict | None = {}
        super().__init__(*args, **kwargs)

    def parse_request(self, *args, **kwargs) -> bool:
        """
        Add additional request parsing steps
        :param args:
        :param kwargs:
        :return:
        """

        if not super().parse_request():  # follow the parent method
            return False

        # parse url params from raw 'self.path'
        self.parsed_url = urlparse(self.path, scheme=URL_SCHEME)
        # self.path = self.parsed_url.path.rstrip("/")
        self.url_params = parse_qs(self.parsed_url.query)

        # parse json from request body
        try:
            body_len = int(self.headers.get("Content-Length"))
            bytes_body = self.rfile.read(body_len)
            self.request_json = json.loads(bytes_body.decode())
        except Exception as e:
            print(f"ERROR: can't parse json from requests body: {e}")
            self.respond_json(code=HTTPStatus.BAD_REQUEST, data=f"can't parse json from requests body: {e}")
            return False  # follow the parent method
            # raise exceptions.BadRequest(detail=f"can't parse json from requests body: {e}")
        else:
            print(f"{self.command} {self.path}")
            return True  # follow the parent method

    # shortcut for responding
    def respond_json(self, code: int, data: str) -> None:
        self.send_response(code=code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(f"{data}".encode())

    def do_GET(self):
        # resources/
        if self.path.startswith("/resources"):
            controller = ResourceController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                res = controller.get()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=f"{e.detail}")
                return

            serializer = ResourceSerializer(res)
            response_string = serializer.serialize()

            self.respond_json(code=HTTPStatus.OK, data=response_string)
            print(f"SUCCESS: sent {res}")

        # resource_types/
        elif self.path.startswith("/resource_types"):
            controller = ResourceTypeController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                res = controller.get()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=f"{e.detail}")
                return

            serializer = ResourceTypeSerializer(res)
            response_string = serializer.serialize()

            self.respond_json(code=HTTPStatus.OK, data=response_string)
            print(f"SUCCESS: sent {res}")

        # url not found
        else:
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

    def do_POST(self):
        # resources/
        if self.path.startswith("/resources"):
            controller = ResourceController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                res = controller.create()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=e.detail)
                return

            serializer = ResourceSerializer(res)
            response_string = serializer.serialize()

            self.respond_json(code=HTTPStatus.CREATED, data=response_string)
            print(f"SUCCESS: sent {res}")

        # resource_types/
        elif self.path.startswith("/resource_types"):
            controller = ResourceTypeController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                res = controller.create()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=e.detail)
                return

            serializer = ResourceTypeSerializer(res)
            response_string = serializer.serialize()

            self.respond_json(code=HTTPStatus.CREATED, data=response_string)
            print(f"SUCCESS: sent {res}")

        # url not found
        else:
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

    def do_DELETE(self):
        # resources/
        if self.path.startswith("/resources"):
            controller = ResourceController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                controller.delete()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=e.detail)
                return

            self.respond_json(code=HTTPStatus.NO_CONTENT, data="")
            print(f"SUCCESS: deleted")

        # resource_types/
        elif self.path.startswith("/resource_types"):
            controller = ResourceTypeController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                controller.delete()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=e.detail)
                return

            self.respond_json(code=HTTPStatus.NO_CONTENT, data="")
            print(f"SUCCESS: deleted")

        # url not found
        else:
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

    def do_PATCH(self):
        # resources/
        if self.path.startswith("/resources"):
            controller = ResourceController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                controller.update()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=e.detail)
                return

            self.respond_json(code=HTTPStatus.CREATED, data="")
            print(f"SUCCESS: resource updated")

        # resource_types/
        elif self.path.startswith("/resource_types"):
            controller = ResourceTypeController(
                path=self.path,
                req_body=self.request_json,
                url_params=self.url_params,
            )
            try:
                controller.update()
            except exceptions.HTTPException as e:
                self.respond_json(code=e.status_code, data=e.detail)
                return

            self.respond_json(code=HTTPStatus.CREATED, data="")
            print(f"SUCCESS: resource_type updated")

        # url not found
        else:
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")


def create_app():
    return HTTPServer(("0.0.0.0", 8000), RequestHandler)


app = create_app()
loop = asyncio.get_event_loop()
loop.run_until_complete(app.serve_forever())
