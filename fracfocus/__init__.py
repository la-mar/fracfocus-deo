# pylint: disable=unused-argument


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate

from config import APP_SETTINGS
import loggers

loggers.config()


# instantiate the extensions
db = SQLAlchemy()
toolbar = DebugToolbarExtension()
migrate = Migrate()


def create_app(script_info=None):
    app = Flask(__name__)
    app.config.from_object(APP_SETTINGS)

    # set up extensions
    db.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)

    from api.completion import comp_blueprint

    # register blueprints
    app.register_blueprint(comp_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():  # pylint: disable=unused-variable
        return {"app": app, "db": db}

    return app

