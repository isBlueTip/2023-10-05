# move out repeating controllers code
# another db access layer - adapters, accept and return Python types
# catch errors from db connection, add more details and pass it further to more specific http errors
# add proper validation as models methods and use everywhere

import asyncio
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pprint import pprint
from typing import List
from urllib.parse import parse_qs, urlparse

from ipdb import set_trace

import exceptions
from controllers import ResourceController, ResourceTypeController
from views import ResourceTypeView, ResourceView

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
        Add additional request parsing steps.

        :param args:
        :param kwargs:
        :return:
        """

        if not super().parse_request():  # follow the parent method
            return False

        # parse url params from raw 'self.path'
        self.parsed_url = urlparse(self.path, scheme=URL_SCHEME)
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
        else:
            print(f"{self.command} {self.path}")
            return True  # follow the parent method

    def respond_json(self, code: int, data: str) -> None:
        """
        Respond to a requesting client.

        :param code:
        :param data:
        :return:
        """

        self.send_response(code=code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(f"{data}".encode())

    def get_controller(self):
        """
        Return a controller instance depending on requested path.

        :return:
        """

        # /resources
        if self.path.startswith("/resources"):
            return ResourceController(
                url=self.parsed_url,
                request_json=self.request_json,
                url_params=self.url_params,
            )

        # /resource_types
        elif self.path.startswith("/resource_types"):
            return ResourceTypeController(
                url=self.parsed_url,
                request_json=self.request_json,
                url_params=self.url_params,
            )

        # not found
        else:
            return None

    def get_view(self, data: List):
        """
        Return a serializer class depending on requested path.

        :return:
        """

        # /resources
        if self.path.startswith("/resources"):
            return ResourceView(data)

        # /resource_types
        elif self.path.startswith("/resource_types"):
            return ResourceTypeView(data)

        # not found
        else:
            return None

    def do_GET(self):
        controller = self.get_controller()

        if not controller:  # url not found
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

        # call specific method handler
        try:
            data = controller.retrieve()
        except exceptions.HTTPException as e:
            self.respond_json(code=e.status_code, data=f"{e.detail}")
            return

        view = self.get_view(data)
        response_string = view.serialize()

        self.respond_json(code=HTTPStatus.OK, data=response_string)
        print(f"SUCCESS: sent {data}")

    def do_POST(self):
        controller = self.get_controller()

        if not controller:  # url not found
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

        # call specific method handler
        try:
            data = controller.create()
        except exceptions.HTTPException as e:
            self.respond_json(code=e.status_code, data=e.detail)
            return

        view = self.get_view(data)
        response_string = view.serialize()

        self.respond_json(code=HTTPStatus.CREATED, data=response_string)
        print(f"SUCCESS: sent {data}")

    def do_PATCH(self):
        controller = self.get_controller()

        if not controller:  # url not found
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

        # call specific method handler
        try:
            data = controller.update()
        except exceptions.HTTPException as e:
            self.respond_json(code=e.status_code, data=e.detail)
            return

        view = self.get_view(data)
        response_string = view.serialize()

        self.respond_json(code=HTTPStatus.CREATED, data=response_string)
        print(f"SUCCESS: {data} updated")

    def do_DELETE(self):
        controller = self.get_controller()

        if not controller:  # url not found
            self.respond_json(code=HTTPStatus.NOT_FOUND, data="resource not found")
            print(f"WARNING: 404 resource not found")

        # call specific method handler
        try:
            controller.delete()
        except exceptions.HTTPException as e:
            self.respond_json(code=e.status_code, data=e.detail)
            return

        self.respond_json(code=HTTPStatus.NO_CONTENT, data="")
        print(f"SUCCESS: deleted")


def create_app():
    return HTTPServer(("0.0.0.0", 8000), RequestHandler)


app = create_app()
loop = asyncio.get_event_loop()
loop.run_until_complete(app.serve_forever())
