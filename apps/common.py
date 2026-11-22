from flask import Flask


def create_app(name, hosts):
    app = Flask(name)
    app.config.update(
        MAX_CONTENT_LENGTH=128 * 1024,
        MAX_FORM_MEMORY_SIZE=128 * 1024,
        TRUSTED_HOSTS=hosts + ["localhost", "127.0.0.1", ".svc", ".svc.cluster.local"],
    )

    @app.get("/healthz")
    def health():
        return "ok"

    return app
