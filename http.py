from lib.microdot import Request

def register_routes(app):
    @app.webserver.route("/", methods=["GET"])
    def get(request: Request):
        return {"state": app.ea1500.state["name"]}

    @app.webserver.route("/", methods=["POST"])
    def post(request: Request):
        if not request.headers.get("Authorization","") == f"Bearer {app.storage.get_secret("http.server.auth_token")}":
            return 'Unauthorized', 401
        
        if not request.json:
            return "Bad Request ", 400

        if not request.json.get("state", "") in [x["name"] for x in app.ea1500.presets]:
            return "Bad Request ", 400

        app.ea1500.apply_preset(request.json["state"])
        app.storage.save_persistent_value("current_preset", request.json["state"])
        app.display.draw()
        return {"state": app.storage.get_persistent_value("current_preset")}
    
    @app.webserver.route("/presets", methods=["POST"])
    def presets(request: Request):
        if not request.headers.get("Authorization","") == f"Bearer {app.storage.get_secret("http.server.auth_token")}":
            return 'Unauthorized', 401
        
        if not request.json:
            return "Bad Request ", 400
        
        app.ea1500.configure_presets(request.json["presets"])
        app.storage.save_persistent_value("ea1500.presets", request.json["presets"])
        app.ea1500.apply_preset(app.ea1500.state["name"])
        app.display.draw()
        return {"state": app.storage.get_persistent_value("current_preset")}
