import asyncio
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

from controllers.resource_controller import ResourceController
from controllers.resource_type_controller import ResourceTypeController


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'message': 'Welcome to My Web App!'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        # GET
        elif self.path == '/resources/<id>':
            pass
        # LIST
        elif self.path == '/resources':
            pass
        # GET
        elif self.path == '/resource_types':
            pass
        # LIST
        elif self.path == '/resource_types/<id>':
            pass
        # 404
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        pass


def create_app():
    return HTTPServer(('0.0.0.0', 8000), RequestHandler)


# if __name__ == '__main__':
app = create_app()
loop = asyncio.get_event_loop()
loop.run_until_complete(app.serve_forever())
