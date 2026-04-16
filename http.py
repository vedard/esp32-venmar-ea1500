from lib.microdot import Request, Response

def register_routes(app):
    @app.webserver.route("/", methods=["GET"])
    def get(request: Request):
        return {
            "preset": app.ea1500.state["name"],
            "ip": app.wifi.get_ip(), 
            "mqtt": "Connected" if app.mqtt.connected else "Disconnected"
        }

    @app.webserver.route("/log", methods=["GET"])
    def get_log(request: Request):
        return Response(
            open("app.log", "rb"),
            headers={"Content-Type": "text/plain; charset=UTF-8"},
        )
