import os
import json
import asyncio
import threading
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, jsonify, request

from ..core.memory import Memory, LeadStore, ConversationStore
from ..utils.logger import get_logger

logger = get_logger("ui")

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)
app.secret_key = os.urandom(24)

brain_ref = None
memory_ref = None
leads_ref = None
modules_ref = {}


def create_app(mirror_brain=None):
    global brain_ref, memory_ref, leads_ref, modules_ref
    brain_ref = mirror_brain
    if mirror_brain:
        memory_ref = mirror_brain.memory
        leads_ref = mirror_brain.leads
        modules_ref = mirror_brain.modules
    return app


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/status")
def api_status():
    if not brain_ref:
        return jsonify({"error": "Brain not connected"})
    status = brain_ref.status()
    return jsonify(status)


@app.route("/api/stats")
def api_stats():
    if not leads_ref:
        return jsonify({})
    hot = leads_ref.get_hot_leads()
    all_leads = leads_ref.get_by_status("new")
    warm = leads_ref.get_by_status("warm")
    return jsonify({
        "total_leads": len(all_leads) if all_leads else 0,
        "hot_leads": len(hot) if hot else 0,
        "warm_leads": len(warm) if warm else 0,
        "modules_loaded": len(modules_ref),
        "groups_monitored": 50,
    })


@app.route("/api/leads")
def api_leads():
    if not leads_ref:
        return jsonify([])
    status_filter = request.args.get("status", "")
    if status_filter:
        leads = leads_ref.get_by_status(status_filter)
    else:
        leads = leads_ref.get_hot_leads(0)
    if not leads:
        return jsonify([])
    return jsonify(leads[:20])


@app.route("/api/lead/<int:lead_id>")
def api_lead(lead_id):
    if not leads_ref:
        return jsonify({"error": "not found"})
    lead = leads_ref.get_by_id(lead_id)
    if not lead:
        return jsonify({"error": "not found"})
    return jsonify(lead)


@app.route("/api/modules")
def api_modules():
    return jsonify({
        "total": len(modules_ref),
        "modules": list(modules_ref.keys()),
    })


@app.route("/api/shadow")
def api_shadow():
    shadow = modules_ref.get("shadow_matrix")
    if shadow:
        return jsonify(shadow.get_health_report())
    return jsonify({"primary": {"role": "not loaded"}})


@app.route("/api/warmth")
def api_warmth():
    warmth = modules_ref.get("warmth_protocol")
    if warmth:
        return jsonify(warmth.summary())
    return jsonify({"group_count": 0})


@app.route("/api/competitors")
def api_competitors():
    radar = modules_ref.get("competitor_radar")
    if radar:
        return jsonify(radar.get_competitor_summary())
    return jsonify([])


@app.route("/api/safety")
def api_safety():
    safety = modules_ref.get("safety_guard")
    if safety:
        return jsonify(safety.safety_report())
    return jsonify({"status": "not loaded"})


@app.route("/api/portfolio")
def api_portfolio():
    portfolio = modules_ref.get("portfolio_sniping")
    if portfolio:
        return jsonify(portfolio.match_projects(["web", "app", "ecommerce"]))
    return jsonify([])


@app.route("/api/groups")
def api_groups():
    if not brain_ref:
        return jsonify([])
    groups = brain_ref.groups.get("groups", [])
    return jsonify(groups)


def start_ui(host="0.0.0.0", port=5555, debug=False):
    logger.info(f"Mirro UI starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
