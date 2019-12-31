# fracfocus-deo

Download data from fracfocus.org and persist to a postgres database

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
```
