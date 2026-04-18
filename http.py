import asyncio
import machine

from lib.microdot import Request, Response

def register_routes(app):
    @app.webserver.route("/", methods=["GET"])
    def get(request: Request):
        return {
            "version": app.__version__,
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

    @app.webserver.route("/ota", methods=["POST"])
    def post_ota(request: Request):
        app.storage.save_persistent_value("ota_at_boot", True)

        async def delay_reboot():
            await asyncio.sleep(3)
            machine.reset()

        asyncio.create_task(delay_reboot())

        return {
            "message": "OTA started; device will reboot multiple times",
        }
