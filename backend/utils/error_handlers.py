"""
Global Application Error Handlers.
Registers JSON error responders for standard HTTP errors and unhandled exceptions.
"""

import logging
from backend.utils.response import error_response

logger = logging.getLogger("fabricflow.errors")


def register_error_handlers(app):
    """Registers consistent JSON error handlers on the Flask app instance."""
    
    @app.errorhandler(400)
    def bad_request(e):
        msg = getattr(e, "description", "Bad Request: The request could not be processed.")
        return error_response(message=str(msg), status_code=400)

    @app.errorhandler(401)
    def unauthorized(e):
        msg = getattr(e, "description", "Unauthorized: Authentication token is missing or invalid.")
        return error_response(message=str(msg), status_code=401)

    @app.errorhandler(403)
    def forbidden(e):
        msg = getattr(e, "description", "Forbidden: You do not have permission to access this resource.")
        return error_response(message=str(msg), status_code=403)

    @app.errorhandler(404)
    def not_found(e):
        msg = getattr(e, "description", "Endpoint or resource not found.")
        return error_response(message=str(msg), status_code=404)

    @app.errorhandler(409)
    def conflict(e):
        msg = getattr(e, "description", "Conflict: The resource already exists or conflict occurred.")
        return error_response(message=str(msg), status_code=409)

    @app.errorhandler(422)
    def unprocessable_entity(e):
        msg = getattr(e, "description", "Unprocessable Entity: Validation failed.")
        return error_response(message=str(msg), status_code=422)

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}", exc_info=True)
        return error_response(message="Internal Server Error: Please try again later.", status_code=500)

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.error(f"Unhandled exception caught: {e}", exc_info=True)
        return error_response(message="An unexpected server error occurred.", status_code=500)
