import hmac
import os

from flask import abort, redirect, render_template, request, session, current_app

from storage import LIMIT, MIN_WORDS, read_article, revision, save_article, word_count

PUBLIC_ORIGIN = os.environ.get("PUBLIC_ORIGIN", "http://www.iam-039.com").rstrip("/")


def matches(value, expected):
    return hmac.compare_digest(value.encode("utf-8"), expected.encode("utf-8"))


def edit():
    text = read_article()
    previous_revision = revision(text)
    error = None
    status = 200
    if request.method == "POST":
        if not matches(request.form.get("csrf", ""), session["csrf"]):
            abort(400)
        text = request.form.get("article", "").strip()
        previous_revision = request.form.get("revision", "")
        if not MIN_WORDS <= word_count(text) <= LIMIT:
            error = f"กรุณากรอกเนื้อหาตั้งแต่ {MIN_WORDS} ถึง {LIMIT} คำ"
            status = 422
        elif not save_article(text, previous_revision):
            error = "เนื้อหาถูกแก้ไขระหว่างที่คุณเปิดหน้านี้ กรุณาคัดลอกข้อความที่แก้ไขไว้ แล้วโหลดหน้าฟอร์มใหม่"
            status = 409
        else:
            return redirect(PUBLIC_ORIGIN + "/research", code=303)

    response = current_app.make_response((render_template(
        "editor.html", article=text, revision=previous_revision, csrf=session["csrf"],
        limit=LIMIT, minimum=MIN_WORDS, error=error, public_url=PUBLIC_ORIGIN + "/research",
    ), status))
    response.headers["Cache-Control"] = "no-store"
    return response
