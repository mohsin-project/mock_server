import json
import os
from multiprocessing import Process

from dotenv import load_dotenv
from flask import Flask, make_response
from flask_cors import CORS

import util

load_dotenv()
import service

server: dict = json.load(open(os.environ["SERVER"]))

app = Flask(__name__)
CORS(app)

HTTP_METHODS = [
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
]


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=HTTP_METHODS)
def api_handler(path):
    return service.handle_request()


@app.errorhandler(Exception)
def handle_exception(error):
    return make_response(str(error), 500)


def run_app(port):
    app.run(host=os.environ["HOST"], port=port)


if __name__ == "__main__":
    ports = server.keys()
    try:
        processes = []
        for port in ports:
            process = Process(target=run_app, args=(port,))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()
    except Exception:
        pass

    util.close_ports(ports)
