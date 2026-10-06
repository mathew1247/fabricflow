"""
FABRICFLOW ANALYTICS - FLASK BACKEND APPLICATION
Production-ready REST API backend connected to Firebase Cloud Firestore and Pandas Analytics.
"""

import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from firebase.firebase_config import init_firebase, check_firestore_connection
from backend.utils.error_handlers import register_error_handlers
from backend.routes import (
    auth_bp,
    product_bp,
    category_bp,
    inventory_bp,
    sales_bp,
    supplier_bp,
    dashboard_bp,
    analytics_bp,
    forecast_bp,
    report_bp
)


def create_app():
    """Application Factory for FabricFlow Analytics."""
    root_dir = os.path.abspath(os.path.dirname(__file__))
    frontend_dir = os.path.join(root_dir, "frontend") if os.path.exists(os.path.join(root_dir, "frontend")) else root_dir
    
    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path=""
    )
    app.config.from_object(Config)

    # Enable Cross-Origin Resource Sharing with configurable origins
    cors_origins = os.environ.get("CORS_ORIGINS", "*")
    if cors_origins != "*" and "," in cors_origins:
        cors_origins = [o.strip() for o in cors_origins.split(",")]
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Initialize Firebase Cloud Firestore
    init_firebase()

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(forecast_bp)
    app.register_blueprint(report_bp)

    # Register Global Consistent Error Handlers
    register_error_handlers(app)

    # Serve Root and Static Frontend Files
    @app.route("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/pages/<path:filename>")
    def serve_pages(filename):
        return send_from_directory(os.path.join(frontend_dir, "pages"), filename)

    @app.route("/css/<path:filename>")
    def serve_css(filename):
        return send_from_directory(os.path.join(frontend_dir, "css"), filename)

    @app.route("/js/<path:filename>")
    def serve_js(filename):
        return send_from_directory(os.path.join(frontend_dir, "js"), filename)

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(os.path.join(frontend_dir, "assets"), filename)

    # Friendly Navigation Routes
    @app.route("/dashboard")
    def page_dashboard():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "dashboard.html")

    @app.route("/products")
    def page_products():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "products.html")

    @app.route("/inventory")
    def page_inventory():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "inventory.html")

    @app.route("/sales")
    def page_sales():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "sales.html")

    @app.route("/suppliers")
    def page_suppliers():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "suppliers.html")

    @app.route("/analytics")
    def page_analytics():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "analytics.html")

    @app.route("/forecast")
    def page_forecast():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "forecast.html")

    @app.route("/reports")
    def page_reports():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "reports.html")

    @app.route("/settings")
    def page_settings():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "settings.html")

    @app.route("/login")
    def page_login():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "login.html")

    # API Health Check Endpoint - Tests live Firestore connectivity
    @app.route("/api/health")
    def health_check():
        is_connected, details = check_firestore_connection()
        if is_connected:
            return jsonify({
                "success": True,
                "status": "healthy",
                "message": "FabricFlow backend is running",
                "firebase": "connected",
                "service": "FabricFlow Analytics API",
                "version": "1.0.0"
            }), 200
        else:
            return jsonify({
                "success": False,
                "status": "unhealthy",
                "message": f"FabricFlow backend running, but Firestore check failed: {details}",
                "firebase": "disconnected",
                "service": "FabricFlow Analytics API",
                "version": "1.0.0"
            }), 503

    return app


app = create_app()

if __name__ == "__main__":
    print("==================================================")
    print("  FABRICFLOW ANALYTICS - FLASK BACKEND SERVER    ")
    print(f"  Running on http://{Config.HOST}:{Config.PORT}")
    print("==================================================")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
