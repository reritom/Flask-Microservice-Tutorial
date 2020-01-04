from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json

def create_application() -> Flask:
    app = Flask(__name__)

    @app.route('/api/<resource_type>', methods=['POST'])
    def post_resource(resource_type):
        # Get the payload from our incoming request
        payload = request.get_json(force=True)

        # Forward the payload to the relevant endpoint in invsys
        response = requests.post(f'invsys:5000/api/{resource_type}', data=json.dumps(payload))

        # Forward the response back to the client
        # We create a Response object by deconstructing our response from above
        return Response(response.content, response.status_code, get_proxy_headers(response))

    @app.route('/api/<resource_type>', methods=['GET'])
    def get_resources(resource_type):
        # There is no payload and no querystrings for this endpoint in invsys
        response = requests.get(f'invsys:5000/api/{resource_type}')

        # Forward the response back to the client
        # We create a Response object by deconstructing our response from above
        return Response(response.content, response.status_code, get_proxy_headers(response))

    return app

def get_proxy_headers(response) -> List[Tuple]:
	  # A function to get the needed headers from the requests response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (name, value)
        for (name, value) in response.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    return headers

if __name__=="__main__":
    app = create_application()
    app.run("0.0.0.0", 5001)
