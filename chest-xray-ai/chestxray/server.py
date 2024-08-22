from base64 import b64decode
from json import loads
from logging import ERROR, getLogger
from sys import modules

from flask import Flask, render_template, request

from .tunnel import start_tunnel
from .xray import XrayScanner

modules["flask.cli"].show_server_banner = lambda *args: None
getLogger("werkzeug").setLevel(ERROR)

app = Flask("")
xray = XrayScanner()


@app.route("/")
def home_page() -> str:
    """Home page of website, lets users quickly access different features"""
    return render_template("home.html")


@app.route("/start-scan")
def start_scan() -> str:
    """Home page of website, lets users quickly access different features"""
    return render_template("scan.html")


@app.route("/result")
def result() -> str:
    """Shows the results of the scan"""
    return render_template("result.html")


@app.route("/api/scan-xray", methods=["POST"])
def scan_xray() -> str:
    """Scans the provided image and returns the AI's predictions."""
    try:
        image = b64decode(loads(request.data)["image"].split(",", 1)[1])
        response = xray.scan_xray(image)
    except Exception as error:
        response = {"error": str(error)}
    finally:
        print("[server] Sending results\n")
        return str(response).replace("'", "\"")


def start_server(host: str = "0.0.0.0", port: int = 13520) -> None:
    """
    Server for webclient, can recieve and scan images.

    Args:
        host: Host address.
        port: Port number.
    """
    alternate_link = f" (http://localhost:{port})" if host == "0.0.0.0" else ""
    print(f"[server] Running locally at http://{host}:{port}{alternate_link}")
    start_tunnel(host, port)
    app.run(host, port)
