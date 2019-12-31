# pylint: disable=not-an-iterable, no-member, arguments-differ
from typing import Dict, List, Tuple, Union, no_type_check
import logging

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

import api.schema as schemas
from api.models import Registry

logger = logging.getLogger(__name__)

well_blueprint = Blueprint("wells", __name__, url_prefix="/wells")
api = Api(well_blueprint)


class DataResource(Resource):
    data_key: Union[str, None] = None
    models: Union[List, None] = None

    @no_type_check
    def get_records(self, **kwargs) -> List[Dict]:
        """ Search each model in self.models for results fitting the given criteria. Once results are found in a model, no subsequent models are searched. Models are searched in order as specified in self.models."""
        for model in self.models:
            result = model.query.get(**kwargs)
            if result:
                return result

    def _get(self, **kwargs) -> Dict:
        data = self.get_records(**kwargs)
        logger.debug(f"retrieved data: {data}")

        if self.data_key:
            data = [getattr(d, self.data_key) for d in data]

        response_object = {
            "status": "success",
            "data": self.schema.dump(data),
        }
        if not response_object.get("data"):
            response_object["status"] = "not_found"

        return response_object


class WellResource(DataResource):
    models = [Registry]

    def get(self, api14: str) -> Tuple[Dict, int]:
        return self._get(api14=api14), 200


class WellListResource(WellResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api14 = request.args.get("api14")
        if api14:
            return self._get(api14__in=str(api14).split(",")), 200
        else:
            return {"status": "missing_argument"}, 400


class Well(WellResource):
    """ All data for a well """

    schema = schemas.WellFullSchema(many=True)


class Wells(WellListResource):
    """ All data for a list of wells """

    schema = schemas.WellFullSchema(many=True)


class Test(WellResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        return request.args, 200


api.add_resource(Test, "/test")
api.add_resource(Wells, "/")
api.add_resource(WellIDList, "/ids")
api.add_resource(HorizontalWellIDs, "/ids/h/<area>")
api.add_resource(VerticalWellIDs, "/ids/v/<area>")
api.add_resource(WellHeaderList, "/headers")
api.add_resource(WellIPTestList, "/ips")
api.add_resource(WellSurveyList, "/surveys")
api.add_resource(WellFracList, "/fracs")
api.add_resource(Well, "/<api14>")
api.add_resource(WellHeader, "/<api14>/header")
api.add_resource(WellIPTest, "/<api14>/ip")
api.add_resource(WellSurvey, "/<api14>/survey")
api.add_resource(WellFrac, "/<api14>/frac")


if __name__ == "__main__":
    from ihs import create_app
    from config import get_active_config

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    model = WellHorizontal
    api14 = "42461409160000"

    apis = [api14, "42461411260000", "42461411600000"]
    many = model.get(api14__in=apis)
