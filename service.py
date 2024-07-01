import json
import os
import re
from urllib import parse

from flask import request, make_response

ENDPOINT_NOT_FOUND = "Could not find mocked endpoint"

server: dict = json.load(open(os.environ['SERVER']))


def path_parts(path):
    return list(filter(None, re.split('/+', path)))


def format_group(string: str):
    match = re.finditer(r"\{(?P<group>\w+)}", string)
    for match in match:
        string = string.replace(match.group(), f"(?P<{match.group('group')}>\\w+)")
    return string


def has_status(obj):
    if "status" in obj:
        return obj
    raise Exception(ENDPOINT_NOT_FOUND)


def find(url_parts, server_obj, params, url_parts_read=0):
    i = url_parts_read
    for sv_key in server_obj:
        sv_key_parts = path_parts(sv_key)
        temp_params = dict(params)

        j = i
        for sv_key_part in sv_key_parts:
            try:
                match = re.match(format_group(sv_key_part), url_parts[j])
                if match:
                    temp_params.update(match.groupdict())
                    j += 1
            except IndexError:
                j = -1
                break

        if j == (i + len(sv_key_parts)):
            params.update(temp_params)
            if j == len(url_parts):
                return has_status(server_obj[sv_key])
            return find(url_parts, server_obj[sv_key], params, j)

    if url_parts_read >= len(url_parts):
        return has_status(server_obj)
    raise Exception(ENDPOINT_NOT_FOUND)


def get_response_body(response):
    body, file = response.get('body'), response.get('file')
    if body:
        return json.dumps(body)
    elif file:
        with open(file, 'r', encoding='unicode_escape') as f:
            try:
                return json.dumps(json.load(f))
            except Exception as e:
                f.seek(0)
                return json.dumps(f.read())
    return ""


def replace_params(string, params: dict):
    for key, value in params.items():
        string = re.sub(f"{{{key}}}", value, string)
    return string


def replace_escaped(string: str):
    escape_sequence = {
        r'\\\\{': r'{',
        r'\\\\}': r'}'
    }

    for sequence, replacement in escape_sequence.items():
        string = re.sub(sequence, replacement, string)

    return string


def handle_request():
    url_path = request.base_url.split(f"{os.environ['HOST']}:")[-1]
    query_params = dict(parse.parse_qsl(parse.urlsplit(request.url).query))
    path_params = {}

    response = find(path_parts(url_path), server, path_params)
    response_body = get_response_body(response)

    if response_body:
        response_body = replace_params(response_body, {**path_params, **query_params})
        response_body = replace_escaped(response_body)
        response_body = json.loads(response_body)

    return make_response(response_body, response.get('status'))
