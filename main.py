import json
import os
from multiprocessing import Process

from dotenv import load_dotenv
from flask import Flask, make_response
from flask_cors import CORS

load_dotenv()
import service

server: dict = json.load(open(os.environ['SERVER']))

app = Flask(__name__)
CORS(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def test_api(path):
    return service.handle_request()


@app.errorhandler(Exception)
def handle_foo_exception(error):
    print(error)
    return make_response(str(error), 500)


def run_app(port):
    app.run(host=os.environ['HOST'], port=port)


if __name__ == '__main__':
    try:
        processes = []
        for port in server.keys():
            process = Process(target=run_app, args=(port,))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()
    except KeyboardInterrupt:
        pass
