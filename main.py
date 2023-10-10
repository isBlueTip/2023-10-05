import asyncio
import http
import json
from http import HTTPStatus  # todo replace with custom exceptions statuses?
from http.server import BaseHTTPRequestHandler, HTTPServer
from pprint import pprint
from urllib.parse import parse_qs, urlparse
from wsgiref.simple_server import make_server

import ipdb

import exceptions
from controllers import ResourceController, ResourceTypeController
from db.models import Resource, ResourceType
from services.resource_service import ResourceService
from services.resource_type_service import ResourceTypeService
from views import ResourceSerializer, ResourceTypeSerializer

# # Mock database data (in-memory)
# resources = [
#     {"id": 1, "name": "Resource1", "type": "Type1", "speed": 60},
#     {"id": 2, "name": "Resource2", "type": "Type2", "speed": 80},
# ]
#
# resource_types = [
#     {"name": "Type1", "max_speed": 100},
#     {"name": "Type2", "max_speed": 120},
# ]
#
#
# def get_resources(environ, start_response):
#     status = "200 OK"
#     headers = [("Content-type", "application/json")]
#
#     query_string = environ.get("QUERY_STRING", "")
#     query_params = parse_qs(query_string)
#
#     if "type" in query_params:
#         resource_type = query_params["type"][0]
#         filtered_resources = [r for r in resources if r["type"] == resource_type]
#     else:
#         filtered_resources = resources
#
#     response_data = json.dumps(filtered_resources).encode("utf-8")
#
#     start_response(status, headers)
#     return [response_data]
#
#
# def create_resource(environ, start_response):
#     # Extract data from the request
#     content_length = int(environ.get("CONTENT_LENGTH", 0))
#     request_body = environ["wsgi.input"].read(content_length)
#     data = json.loads(request_body.decode("utf-8"))
#
#     # Mock database insert (in-memory)
#     new_resource = {
#         "id": len(resources) + 1,
#         "name": data["name"],
#         "type": data["type"],
#         "speed": data["speed"],
#     }
#     resources.append(new_resource)
#
#     status = "201 Created"
#     headers = [("Content-type", "application/json")]
#
#     response_data = json.dumps(new_resource).encode("utf-8")
#
#     start_response(status, headers)
#     return [response_data]
#
#
# def app(environ, start_response):
#     path = environ["PATH_INFO"]
#
#     if path == "/resources" and environ["REQUEST_METHOD"] == "GET":
#         return get_resources(environ, start_response)
#     elif path == "/resources" and environ["REQUEST_METHOD"] == "POST":
#         return create_resource(environ, start_response)
#     else:
#         status = "404 Not Found"
#         headers = [("Content-type", "text/plain")]
#         start_response(status, headers)
#         return [b"Not Found"]
#
#
# # if __name__ == "__main__":
# #     with make_server("", 8000, app) as httpd:
# #         print("Serving on port 8000...")
# #         httpd.serve_forever()


# /*************************************************************/


# """A barebones ASGI app that dumps scope."""
#
# import pprint
#
#
# def pretty_html_bytes(obj):
#     """Pretty print a Python object in <pre> tags."""
#     pp = pprint.PrettyPrinter(indent=2, width=256)
#     prettified = pp.pformat(obj)
#     return f"<pre>{prettified}</pre>".encode()
#
#
# async def app(scope, receive, send):
#     """The simplest of ASGI apps, displaying scope."""
#     headers = [(b"content-type", b"text/html")]
#     body = pretty_html_bytes(scope)
#     await send({"type": "http.response.start", "status": 200, "headers": headers})
#     await send({"type": "http.response.body", "body": body})
#
#
# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)

URL_SCHEME = "scheme://path;parameters?query#fragment"

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

    def parse_request(self, *args, **kwargs):
        if not super().parse_request():  # follow the parent method
            return False
        self.parsed_url = urlparse(self.path, scheme=URL_SCHEME)
        self.path = self.parsed_url.path.rstrip("/")
        self.url_params = parse_qs(self.parsed_url.query)
        body_len = int(self.headers.get("Content-Length"))
        bytes_body = self.rfile.read(body_len)

        # parse body from request
        try:
            self.req_body = json.loads(bytes_body.decode())
        except Exception:
            raise exceptions.BadRequest(detail="bad body data")
        return True  # follow the parent method

    def do_GET(self):
        print(f"self.command = {self.command}")  # GET
        print(f"self.path = {self.path}")  # /resources/5/?token=121/
        print(f"parsed_url = {self.parsed_url}")  # ParseResult(...)
        print(f"path = {self.path}")  # /resources/5
        print(f"")
        print(f"parsed_url.query = {self.parsed_url.query}")  # token=121/
        print(f"")
        print(f"query_params = {self.url_params}")  # {'token': ['121/']}

        # resources
        if self.path == "/resources":
            print("/resources")
        elif self.path.startswith("/resources/id"):
            print("/resources/")
            # todo try if int else 404
            resource_id = int(self.path.split("/")[-1])
            print(f"resource_id = {resource_id}")

        # resource_types
        elif self.path == "/resource_types":
            print("/resource_types")
        elif self.path.startswith("/resource_types/"):
            print("/resource_types/id")
            controller = ResourceTypeController(
                # db_service=resource_type_service, path=self.path, req_body=self.req_body, url_params=self.url_params
                path=self.path,
                req_body=self.req_body,
                url_params=self.url_params,
            )
            try:
                res = controller.get()
            except exceptions.HTTPException as e:
                # self.send_error(code=e.status_code, message=e.detail)
                self.send_response(code=e.status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(f"{e.detail}".encode())
                return

            print(f"res = {res}")
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    def do_POST(self):
        if self.path == "/resources":
            #         controller = ResourceController(self)
            #         controller.handle_request()
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
            self.send_response(code=http.HTTPStatus.CREATED)
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
            self.send_response(code=http.HTTPStatus.CREATED)
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
