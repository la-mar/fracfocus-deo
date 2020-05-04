""" Entrypoint for WSGI HTTP Server, usually gunicorn """
from gevent import monkey

monkey.patch_all()

from fracfocus import create_app


# gunicorn expects the app object to appear under a variable named "application"
application = create_app()
