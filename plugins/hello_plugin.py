"""Sample Hello World & Echo Plugin"""
ALLOWED_METHODS = ["GET", "POST"]

def handle_request(method, query_params, body_payload):
    if method == "POST":
        return {
            "plugin": "hello_plugin",
            "message": "Processed POST data",
            "received": body_payload
        }
    return {
        "plugin": "hello_plugin",
        "message": "Hello from dynamically plugged-in framework module!",
        "params": query_params
    }
