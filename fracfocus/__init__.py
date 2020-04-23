

import time
import random
import logging

from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate


from config import get_active_config, APP_SETTINGS
import loggers
from util import ensure_list
from util.dt import utcnow
import shortuuid

conf = get_active_config()

loggers.config()

logger = logging.getLogger("app.access")


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

    @app.before_request
    def before_request():
        g.start = time.time()
        request.id = shortuuid.uuid()
        request.should_log = (
            random.random() > conf.WEB_LOG_SAMPLE_FRAC
        )  # pairs request/response logs # noqa
        request.arg_counts = {
            k: len(ensure_list(v)) for k, v in (request.args or {}).items()
        }
        request.arg_count_str = "".join(
            [f" {k}s={v}" for k, v in request.arg_counts.items()]
        )

        if conf.WEB_LOG_REQUESTS:
            attrs = {
                "request": {
                    "request_at": utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
                    "remote_addr": request.remote_addr,
                    "method": request.method,
                    "path": request.path,
                    "query_string": request.query_string,
                    "scheme": request.scheme,
                    "referrer": request.referrer,
                    "user_agent": request.user_agent,
                    "headers": request.headers,
                    "args": request.args,
                },
            }

            if request.should_log:
                logger.info(
                    f"[{request.id}] {request.method} - {request.scheme}:{request.path}{request.arg_count_str}",  # noqa
                    extra=attrs,
                )

    @app.after_request
    def after_request(response):
        """ Logging after every request. """

        now = time.time()
        duration = round(now - g.start, 2)

        if conf.WEB_LOG_RESPONSES:
            attrs = {
                "request": {
                    "request_id": request.id,
                    "remote_addr": request.remote_addr,
                    "method": request.method,
                    "path": request.path,
                    "query_string": request.query_string,
                    "scheme": request.scheme,
                    "referrer": request.referrer,
                    "user_agent": request.user_agent,
                    "headers": request.headers,
                    "args": request.args,
                    "arg_counts": request.arg_counts,
                    "duration": duration,
                },
                "response": {
                    "status": response.status,
                    "status_code": response.status_code,
                    "content_length": response.content_length,
                },
            }

        if request.should_log:
            logger.info(
                f"[{request.id}] RESPONSE - {request.scheme}:{request.path}{request.arg_count_str} -> {response.status} ({duration}s)",  # noqa
                extra=attrs,
            )

        return response

    return app
