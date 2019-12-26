# import os
from sqlalchemy.sql import func
from uuid import uuid4

# from fracfocus import db
from api.mixins import DataFrameMixin

schema = "public"

from flask_sqlalchemy import SQLAlchemy


class Test(object):
    def __init__(self):
        _include_sqlalchemy(self, self.__class__)


db: SQLAlchemy = Test()  # <-- add a type hint to let pycharm know what db is.


class IntegrationLog(DataFrameMixin, db.Model):

    __tablename__ = "integration_log"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    integrated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    model_name = db.Column(db.String(), nullable=False)
    inserts = db.Column(db.Integer(), nullable=False, default=0)
    updates = db.Column(db.Integer(), nullable=False, default=0)
    deletes = db.Column(db.Integer(), nullable=False, default=0)
    updated_by = db.Column(db.String(), default=func.current_user(), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class Registry(DataFrameMixin, db.Model):

    __tablename__ = "registry"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    pkey = db.Column(db.models.UUIDField(as_uuid=True, primary_key=True, default=uuid4))
    job_start_Date = db.Column(db.models.DateField(auto_now=False, auto_now_add=False))
    job_end_Date = db.Column(db.models.DateField(auto_now=False, auto_now_add=False))
    # api14 = db.Column(db)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class Ingredients(DataFrameMixin, db.Model):

    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )


class Purpose(DataFrameMixin, db.Model):

    __tablename__ = "purpose"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
