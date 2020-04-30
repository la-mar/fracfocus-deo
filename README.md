# fracfocus-deo

Download data from fracfocus.org and persist to a postgres database

<div style="text-align:center;">
  <table >
    <tr>
      <a href="https://codeclimate.com/github/la-mar/fracfocus-deo/maintainability"><img src="https://api.codeclimate.com/v1/badges/c76108a7a3994ed570e7/maintainability" /></a>
      <a href="https://codecov.io/gh/la-mar/fracfocus-deo">
        <img src="https://codecov.io/gh/la-mar/fracfocus-deo/branch/master/graph/badge.svg" />
      </a>
      <a href="(https://circleci.com/gh/la-mar/fracfocus-deo">
        <img src="https://circleci.com/gh/la-mar/fracfocus-deo.svg?style=svg" />
      </a>
    </tr>
  </table>
</div>

```.env
APP_SETTINGS=fracfocus.config.ProductionConfig
DATABASE_DRIVER=postgres
DATABASE_HOST=YOUR_DATABASE_HOST
DATABASE_NAME=YOUR_DATABASE_NAME
DATABASE_USERNAME=YOUR_DATABASE_USERNAME
DATABASE_PASSWORD=YOUR_DATABASE_PASSWORD
FLASK_APP=fracfocus.manage.py
FLASK_ENV=production
SECRET_KEY=my_precious
GUNICORN_CMD_ARGS="--bind=0.0.0.0:80 --log-level=info --name=gunicorn-fracfocus --timeout=120 --graceful-timeout=120 --worker-class=gevent --workers=3"
```
