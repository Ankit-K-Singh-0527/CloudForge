
from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "service": "CloudForge API",
            "message": "Backend is running successfully",
        }
    ), 200


@health_bp.get("/health/ready")
def readiness_check():
    try:
        db.session.execute(text("SELECT 1"))

        return jsonify(
            {
                "status": "ready",
                "database": "connected",
                "service": "CloudForge API",
            }
        ), 200

    except SQLAlchemyError:
        db.session.rollback()

        return jsonify(
            {
                "status": "not_ready",
                "database": "unavailable",
                "service": "CloudForge API",
            }
        ), 503
