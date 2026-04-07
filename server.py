#this file setup a HTTP server that listens for POST requests at the /api/chat endpoint. The UI frontend sends a request of generating a response to this endpoint
#then the server call the generate_response function from chatbot.py to generate one and return it to the frontend.
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from chatbot import generate_response


class ChatHandler(SimpleHTTPRequestHandler):
    def send_json_headers(self, content_length):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(content_length))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body or b"{}")
            message = payload.get("message", "")
            reply = generate_response(message)
            response_body = json.dumps({"reply": reply}).encode("utf-8")
        except Exception as error:
            response_body = json.dumps({"reply": f"Server error: {error}"}).encode("utf-8")

        self.send_json_headers(len(response_body))
        self.wfile.write(response_body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ChatHandler)
    print("Serving chatbot UI at http://127.0.0.1:8000")
    server.serve_forever()
