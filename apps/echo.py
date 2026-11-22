from flask import render_template

from common import create_app

app = create_app(__name__, ["www.iam-039.com", "iam-039.com"])


@app.get("/api-039", strict_slashes=False)
def instructions():
    return render_template("echo.html", message="พิมพ์ข้อความต่อท้าย /api-039/ ในแถบที่อยู่")


@app.get("/api-039/<path:message>")
def echo(message):
    return render_template("echo.html", message=message)
