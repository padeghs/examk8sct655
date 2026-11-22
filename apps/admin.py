import os
import re
from functools import wraps

from flask import Response, abort, redirect, render_template, request, session

from common import create_app
from editor import edit, matches, PUBLIC_ORIGIN
from storage import profile_revision, read_profile, save_profile

app = create_app(__name__, ["admin.iam-039.com"])
app.config.update(
    SECRET_KEY=os.environ.get("EDITOR_SESSION_KEY"),
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_COOKIE_SECURE=os.environ.get("EDITOR_SECURE_COOKIE") == "true",
)


def login_required(view):
    @wraps(view)
    def authorized(*args, **kwargs):
        username = os.environ.get("EDITOR_USERNAME")
        password = os.environ.get("EDITOR_PASSWORD")
        if not (username and password and app.secret_key):
            abort(503)
        auth = request.authorization
        if (
            auth and auth.type == "basic"
            and matches(auth.username or "", username)
            and matches(auth.password or "", password)
        ):
            session.setdefault("csrf", os.urandom(32).hex())
            return view(*args, **kwargs)
        return Response("Authentication required", 401, {
            "WWW-Authenticate": 'Basic realm="ID039 admin", charset="UTF-8"',
        })
    return authorized


@app.after_request
def prevent_editor_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
@login_required
def dashboard():
    return render_template("admin.html")


app.add_url_rule("/edit/research", view_func=login_required(edit), methods=["GET", "POST"])


@app.route("/edit/portal", methods=["GET", "POST"])
@login_required
def edit_portal():
    profile = read_profile()
    previous_revision = profile_revision(profile)
    error = None
    status = 200
    if request.method == "POST":
        if not matches(request.form.get("csrf", ""), session["csrf"]):
            abort(400)
        profile = {key: request.form.get(key, "").strip() for key in profile}
        previous_revision = request.form.get("revision", "")
        if not 1 <= len(profile["name"]) <= 120 or not re.fullmatch(r"[0-9]{8}", profile["student_id"]):
            error, status = "กรอกชื่อและรหัสนักศึกษา 8 หลัก", 422
        elif not save_profile(profile, previous_revision):
            error, status = "ข้อมูลถูกแก้ไขแล้ว กรุณาโหลดแบบฟอร์มใหม่", 409
        else:
            return redirect(PUBLIC_ORIGIN + "/", code=303)
    return render_template(
        "portal-editor.html", profile=profile, revision=previous_revision,
        csrf=session["csrf"], error=error,
    ), status
