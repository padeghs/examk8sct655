from flask import render_template

from common import create_app
from storage import read_profile

app = create_app(__name__, ["www.iam-039.com"])


@app.get("/")
@app.get("/about", strict_slashes=False)
def portal():
    return render_template("about.html", profile=read_profile())
