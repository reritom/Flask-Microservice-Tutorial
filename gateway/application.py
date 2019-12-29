from flask import Flask, request, Response
import requests
from typing import Optional

def get_relevent_headers(response: requests.models.Response) -> List[tuple]:
    """
    From a reqeusts response, extract the relevent headers for forwarding the response
    """
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (name, value)
        for (name, value) in response.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    return headers

def create_application() -> Flask:
    """
    Create and return an instance of the application
    """
    app = Flask(__name__)

    app.route('/api/resources', methods=['POST'])
    def create_resource():
        response = requests.post('http://invsys:5001/api/resources', data=json.dumps(request.get_json(force=True)))
        return Response(response.content, response.status_code, get_relevent_headers(response))

    return app
