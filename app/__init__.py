from flask import Flask
from .routes import tasks_bp
from .metrics import setup_metrics
 
def create_app():
    app = Flask(__name__)
    app.config['TESTING'] = False
 
    app.register_blueprint(tasks_bp)
    setup_metrics(app)
 
    return app