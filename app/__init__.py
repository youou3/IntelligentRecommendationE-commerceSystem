from flask import Flask, jsonify

from app.api.behavior_api import behavior_bp
from app.api.profile_api import profile_bp
from app.api.recommendation_api import recommendation_bp
from app.api.feedback_api import feedback_bp
from app.api.product_selection_api import product_selection_bp
from app.core.config import DevelopmentConfig
from app.core.database import db, init_mongo


def create_app(config_object=DevelopmentConfig):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_object)

    db.init_app(flask_app)
    init_mongo(flask_app)

    import app.models  # noqa: F401

    flask_app.register_blueprint(behavior_bp)
    flask_app.register_blueprint(profile_bp)
    flask_app.register_blueprint(recommendation_bp)
    flask_app.register_blueprint(feedback_bp)
    flask_app.register_blueprint(product_selection_bp)

    @flask_app.get('/health')
    def health():
        return jsonify({
            'success': True,
            'code': 'OK',
            'message': 'success',
            'request_id': None,
            'data': {'status': 'ok'},
        })

    return flask_app
