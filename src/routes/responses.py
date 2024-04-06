from flask import jsonify, make_response


def create_response(data, status=200):
    return make_response(jsonify({"data": data}), status)

def create_no_content_response():
    return make_response("", 204)

def create_error_response(message, status=400):
    return make_response(jsonify({"error": message}), status)
