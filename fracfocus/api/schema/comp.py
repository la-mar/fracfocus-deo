# pylint: disable=unused-argument

import functools
from datetime import timezone
from typing import Dict, Mapping, Optional, Union

from marshmallow import Schema, fields, post_dump

from api.schema.validators import length_is_10, length_is_14


class CompletionParameterSchema(Schema):
    class Meta:
        ordered = True

    api10 = fields.Str(required=True, validate=length_is_10)
    total_base_water_volume = fields.Int()
    ingredient_mass = fields.Int()
    hf_job_pct = fields.Float()
    water_mass = fields.Int()
    prop_mass = fields.Int()
    mass_diff_pct = fields.Float()
    updated_at = fields.Date()

    @post_dump
    def transform(self, data: Dict, **kwargs) -> Dict:
        data["hf_job_pct"] = self.round_field(data.get("hf_job_pct"))
        data["mass_diff_pct"] = self.round_field(data.get("mass_diff_pct"))
        data["provider"] = "FracFocus"
        return data

    def round_field(self, value: Union[float, None], n: int = 2) -> Optional[float]:
        return round(value, n) if value else None


# if __name__ == "__main__":
#     from fracfocus import create_app, db

#     # from collector import Endpoint
#     import datetime
#     from api.models import Registry

#     app = create_app()
#     app.app_context().push()

#     obj = Registry.query.filter_by(api14="42461409160000").all()
#     obj[0].__dict__

#     cls = Registry

#     api10s = ["4246140916", "4238340637"]
#     api14s = [
#         "42461409160000",
#         "42383406370000",
#     ]
#     ",".join(api14s)

#     results = cls.completion_calcs(api10s)
#     stmt = cls.completion_calcs(api10s, stmt_only=True)

#     schema = CompletionParameterSchema(many=True)

#     schema.dump(results)

#     import sqlalchemy

#     dir(sqlalchemy)
#     sqlalchemy.text(results)
#     dir(stmt)
#     print(str(stmt))
