from flask import render_template

from common import create_app
from storage import display_text, read_article

app = create_app(__name__, ["www.iam-039.com"])


@app.get("/research", strict_slashes=False)
def research():
    return render_template("research.html", article=display_text(read_article()))
