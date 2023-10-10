import asyncio
import json
from http import HTTPStatus  # todo replace with custom exceptions statuses?
from http.server import BaseHTTPRequestHandler, HTTPServer
from pprint import pprint
from urllib.parse import parse_qs, urlparse

from ipdb import set_trace

import exceptions
from controllers import ResourceController, ResourceTypeController
from db.models import Resource, ResourceType
from services.resource_service import ResourceService
from services.resource_type_service import ResourceTypeService
from views import ResourceSerializer, ResourceTypeSerializer

URL_SCHEME = "scheme://path;parameters?query"

resource_service = ResourceService()
resource_type_service = ResourceTypeService()


class RequestHandler(BaseHTTPRequestHandler):
    """
    Main router for the app
    """

    def __init__(self, *args, **kwargs):
        self.parsed_url = ""
        self.url_params = {}
        self.req_body = {}
        super().__init__(*args, **kwargs)

    # @typing.override
    def parse_request(self, *args, **kwargs):
        if not super().parse_request():  # follow the parent method
            return False
        # todo refactor url parsing to 'self.parsed_url'
        self.parsed_url = urlparse(self.path, scheme=URL_SCHEME)
        self.path = self.parsed_url.path.rstrip("/")
        self.path = self.path.strip(" ")
        self.url_params = parse_qs(self.parsed_url.query)
        body_len = int(self.headers.get("Content-Length"))
        bytes_body = self.rfile.read(body_len)

        # print(f"self.command = {self.command}")  # GET
        # print(f"self.path = {self.path}")  # /resources/5/?token=121/
        # print(f"parsed_url = {self.parsed_url}")  # ParseResult(...)
        # print(f"path = {self.path}")  # /resources/5
        # print(f"url_params = {self.url_params}")  # {'token': ['121/']}

        # parse body from request
        try:
            self.req_body = json.loads(bytes_body.decode())
        except Exception as e:
            print(f"ERROR: can't json request body: {e}")
            raise exceptions.BadRequest(detail="bad body data")
        print(f"REQUEST: {self.path}")
        return True  # follow the parent method

    def respond_json(self, code: int, data: str):
        # self.send_error(code=e.status_code, message=e.detail)
        self.send_response(code=code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(f"{data}".encode())

    def do_GET(self):
        # resources/
        if self.path.startswith("/resources"):
            controller = ResourceController(
                path=self.path,
                req_body=self.req_body,
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
                req_body=self.req_body,
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

        # resource not found
        else:
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

    def do_POST(self):
        # resources/
        if self.path == "/resources":
            #         controller = ResourceController(self)
            #         controller.handle_request()
            controller = ResourceController(
                # db_service=resource_type_service, path=self.path, req_body=self.req_body, url_params=self.url_params
                path=self.path,
                req_body=self.req_body,
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
        elif self.path == "/resource_types":
            #         # Create an instance of the ResourceController and handle resource-related routes
            #         controller = ResourceController(self)
            #         controller.handle_request()
            controller = ResourceTypeController(
                # db_service=resource_type_service, path=self.path, req_body=self.req_body, url_params=self.url_params
                path=self.path,
                req_body=self.req_body,
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

        # resource not found
        else:
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

    def do_DELETE(self):
        if self.path == "/resources":
            print("POST /resources")
            controller = ResourceController(
                # db_service=resource_type_service, path=self.path, req_body=self.req_body, url_params=self.url_params
                path=self.path,
                req_body=self.req_body,
                url_params=self.url_params,
            )
            try:
                res = controller.create()
            except exceptions.HTTPException as e:
                # self.send_error(code=e.status_code, message=e.detail)
                self.send_response(code=e.status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(f"{e.detail}".encode())
                return

            serializer = ResourceSerializer(res)
            response_string = serializer.serialize()
            self.send_response(code=HTTPStatus.CREATED)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response_string.encode())

        elif self.path == "/resource_types":
            #         # Create an instance of the ResourceController and handle resource-related routes
            #         controller = ResourceController(self)
            #         controller.handle_request()
            print("POST /resource_types")
            controller = ResourceTypeController(
                # db_service=resource_type_service, path=self.path, req_body=self.req_body, url_params=self.url_params
                path=self.path,
                req_body=self.req_body,
                url_params=self.url_params,
            )
            try:
                res = controller.create()
            except exceptions.HTTPException as e:
                # self.send_error(code=e.status_code, message=e.detail)
                self.send_response(code=e.status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(f"{e.detail}".encode())
                return

            serializer = ResourceTypeSerializer(res)
            response_string = serializer.serialize()
            self.send_response(code=HTTPStatus.CREATED)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response_string.encode())

        # Resource not found
        else:
            self.send_response(code=HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "application/json")
            self.end_headers()


def create_app():
    return HTTPServer(("0.0.0.0", 8000), RequestHandler)


# if __name__ == '__main__':
app = create_app()
loop = asyncio.get_event_loop()
loop.run_until_complete(app.serve_forever())
