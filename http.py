from lib.microdot import Request

def register_routes(app):
    @app.webserver.route("/", methods=["GET"])
    def get(request: Request):
        return {
            "mode": app.ea1500.state["name"], 
            "ip": app.wifi.get_ip(), 
            "mqtt": "Connected" if app.mqtt.connected else "Disconnected"
        }