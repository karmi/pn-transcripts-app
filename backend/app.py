from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory, abort

from config import load_config
from storage import r2_client, get_audio_url, get_transcript

CONFIG_PATH = os.environ.get("CONFIG_PATH", "data/config.yml")
R2_KEY = os.environ["R2_ACCESS_KEY_ID"]
R2_SECRET = os.environ["R2_SECRET_ACCESS_KEY"]

ALLOWED_ORIGINS = {
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
}

cfg = load_config(CONFIG_PATH)
s3 = r2_client(cfg.r2.endpoint, R2_KEY, R2_SECRET)


def create_app():
    app = Flask(
        __name__,
        static_folder="../frontend/dist/assets",
        static_url_path="/assets",
    )
    app.json.ensure_ascii = False

    DIST_ROOT = Path(app.root_path).parent / "frontend" / "dist"

    @app.after_request
    def _headers(resp):
        resp.headers["X-Robots-Tag"] = "noindex, nofollow"
        if request.path.startswith("/media/"):
            resp.headers["Cache-Control"] = "no-store"
        else:
            resp.headers["Cache-Control"] = (
                "public, max-age=300, stale-while-revalidate=86400"
            )

        # CORS
        origin = request.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            resp.headers["Access-Control-Allow-Origin"] = (
                origin  # echo back the actual origin
            )
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
        return resp

    @app.get("/health")
    def _health():
        return "OK\n", 200, {"Cache-Control": "no-store"}

    @app.get("/api/items")
    def items():
        return jsonify([vars(it) for it in cfg.items])

    @app.get("/api/items/<item_id>")
    def item_detail(item_id: str):
        item = next((it for it in cfg.items if it.id == item_id), None)
        if not item:
            return jsonify({"error": "not found"}), 404
        raw = get_transcript(s3, cfg.r2.bucket_text, item_id)
        return jsonify({"item": vars(item), "transcript": raw})

    @app.get("/media/<item_id>")
    def media(item_id: str):
        url = get_audio_url(s3, cfg.r2.bucket_audio, item_id, ttl=90)
        return redirect(url, code=302)

    @app.route("/api/<path:_any>", methods=["OPTIONS"])
    def _options_api(_any):
        return ("", 204)

    @app.route("/media/<path:_any>", methods=["OPTIONS"])
    def _options_media(_any):
        return ("", 204)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa_fallback(path: str):
        # Let API and media routes (and anything else you explicitly handle) pass through
        if path.startswith("api/") or path.startswith("media/"):
            abort(404)

        # Serve actual static assets if they exist (js/css/png, etc.)
        candidate = DIST_ROOT / path
        if path and candidate.exists():
            return send_from_directory(DIST_ROOT, path)

        # Otherwise, return the SPA shell
        return send_from_directory(DIST_ROOT, "index.html")

    return app


app = create_app()
