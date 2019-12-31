# pylint: disable=unused-argument

from typing import Dict, Mapping, Union, Optional
import functools
from datetime import timezone

from marshmallow import Schema, fields, post_dump

from api.schema.validators import length_is_14, length_is_10

from api.models import Registry


class WellSchema(Schema):
    class Meta:
        ordered = True

    api10 = fields.Str(required=True, validate=length_is_10)
    total_base_water_volume = fields.Int()
    ingredient_mass = fields.Int()
    percent_hf_job = fields.Float()
    water_mass = fields.Int()
    prop_mass = fields.Int()
    mass_diff_pct = fields.Float()

    @post_dump
    def transform(self, data: Dict, **kwargs) -> Dict:
        data["percent_hf_job"] = self.round_field(data.get("percent_hf_job"))
        data["mass_diff_pct"] = self.round_field(data.get("mass_diff_pct"))
        return data

    def round_field(self, value: Union[float, None], n: int = 2) -> Optional[float]:
        return round(value, n) if value else None


if __name__ == "__main__":
    from fracfocus import create_app, db

    # from collector import Endpoint
    import datetime

    app = create_app()
    app.app_context().push()

    obj = Registry.query.filter_by(api14="42173367050000").all()
    len(obj)

    cls = Registry

    api10s = ["4217336705", "4247537815"]

    results = cls.completion_calcs(api10s)

    schema = WellSchema(many=True)

    schema.dump(results)

