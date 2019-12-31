from typing import List, Dict, NewType, Union
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import Integer, Float
import uuid
import logging

from fracfocus import db
from api.mixins import CoreMixin
import util
import util.deco

logger = logging.getLogger(__name__)

schema = "public"

WATER_LBS_PER_GALLON = 8.33
PROPPANT_REGEX = "sand|silica|propp|mesh"


class Registry(CoreMixin, db.Model):

    __tablename__ = "registry"

    upload_key = db.Column(UUID(as_uuid=True), primary_key=True)
    job_start_date = db.Column(db.Date)
    job_end_date = db.Column(db.Date)
    api14 = db.Column(db.String(14), index=True)
    api10 = db.Column(db.String(10), index=True)
    state_no = db.Column(db.Integer())
    county_no = db.Column(db.Integer())
    operator = db.Column(db.String())
    well_name = db.Column(db.String())
    lat = db.Column(db.Float())
    lon = db.Column(db.Float())
    proj = db.Column(db.String())
    tvd = db.Column(db.Integer())
    total_base_water_volume = db.Column(db.BigInteger())
    total_base_non_water_volume = db.Column(db.BigInteger())
    state = db.Column(db.String())
    county = db.Column(db.String())
    ff_version = db.Column(db.String())
    is_federal_well = db.Column(db.Boolean(), default=False)
    is_indian_well = db.Column(db.Boolean(), default=False)
    source = db.Column(db.String())
    dtmod = db.Column(db.String())
    purpose_key = db.Column(UUID(as_uuid=True))
    trade_name = db.Column(db.String())
    supplier = db.Column(db.String())
    purpose = db.Column(db.String())
    system_approach = db.Column(db.Boolean())
    is_water = db.Column(db.Boolean())
    purpose_percent_hf_job = db.Column(db.Float())
    purpose_ingredient_msds = db.Column(db.Boolean(), default=False)
    ingredient_key = db.Column(UUID(as_uuid=True), primary_key=True)
    ingredient_name = db.Column(db.String())
    cas_number = db.Column(db.String())
    percent_high_additive = db.Column(db.Float())
    percent_hf_job = db.Column(db.Float())
    ingredient_comment = db.Column(db.String())
    ingredient_msds = db.Column(db.Boolean(), default=False)
    ingredient_mass = db.Column(db.BigInteger())
    claimant_company = db.Column(db.String())
    disclosure_key = db.Column(UUID(as_uuid=True))

    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False,
    )

    @classmethod
    def completion_calcs(
        cls, api10s: List[str], stmt_only: bool = False
    ) -> List[Dict[str, Union[str, int, float]]]:
        agg = (
            cls.query.with_entities(
                cls.api10,
                func.max(cls.total_base_water_volume).label("total_base_water_volume"),
                func.sum(cls.ingredient_mass).cast(Integer).label("ingredient_mass"),
                (func.sum(cls.percent_hf_job) / 100).label("percent_hf_job"),
            )
            .filter(cls.ingredient_name.op("~*")(PROPPANT_REGEX))
            .filter(cls.api10.in_(api10s))
            .group_by(cls.api10)
            .subquery()
        )

        agg2 = (
            cls.s.query(agg)
            .with_entities(
                agg,
                (agg.c.total_base_water_volume * WATER_LBS_PER_GALLON).label(
                    "water_mass"
                ),
            )
            .subquery()
        )

        agg3 = (
            cls.s.query(agg2)
            .with_entities(
                agg2,
                ((agg2.c.water_mass * agg2.c.percent_hf_job / 100)).label("prop_mass"),
            )
            .subquery()
        )

        agg4 = (
            cls.s.query(agg3)
            .with_entities(
                agg3,
                (
                    (agg3.c.prop_mass - agg3.c.ingredient_mass) / agg3.c.ingredient_mass
                ).label("mass_diff_pct"),
            )
            .subquery()
        )

        qry = cls.s.query(agg4)
        if stmt_only:
            return qry.statement
        return [x._asdict() for x in qry.all()]


if __name__ == "__main__":
    from fracfocus import create_app, db
    import datetime

    app = create_app()
    app.app_context().push()

    cls = Registry

    # cls.completion_calcs(api10="4217336705")

    api10s = ["4217336705", "4247537815"]

    # cls.s.rollback()

    cls.completion_calcs(api10s)
