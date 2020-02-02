# pylint: disable=not-an-iterable, no-member, arguments-differ, invalid-name, no-value-for-parameter
from typing import Dict, List, Tuple, Union, no_type_check
import logging

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

import api.schema as schemas
from api.models import Registry

logger = logging.getLogger(__name__)

comp_blueprint = Blueprint("completions", __name__)
api = Api(comp_blueprint)


class CompletionResource(Resource):
    schema = schemas.CompletionParameterSchema

    def get(self, api10: str) -> Tuple[Dict, int]:
        if len(api10) != 10:
            return {
                "status": f"api should have a length of 10. The passed parameter has a length of {len(api10)} ({api10})."
            }
        result = Registry.completion_calcs(api10s=[api10])
        return self.schema.dump(result), 200


class CompletionListResource(Resource):
    schema = schemas.CompletionParameterSchema

    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api10 = request.args.get("api10")
        if api10:
            result = Registry.completion_calcs(api10s=str(api10).split(","))
            return self.schema.dump(result), 200
        else:
            return {"status": "missing_argument"}, 400


class Completion(CompletionResource):
    """ All data for a completion """

    schema = schemas.CompletionParameterSchema(many=True)


class Completions(CompletionListResource):
    """ All data for a list of completions """

    schema = schemas.CompletionParameterSchema(many=True)


class Test(CompletionResource):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        return request.args, 200


api.add_resource(Test, "/test")
api.add_resource(Completions, "/")
api.add_resource(Completion, "/<api10>")


if __name__ == "__main__":
    from fracfocus import create_app
    from config import get_active_config

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    api10s = ["4246140916"]
    Registry.completion_calcs(api10s=api10s)
    Registry.query.filter(Registry.api10.in_(api10s)).all()
