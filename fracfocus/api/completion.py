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


class Completion10(Resource):
    schema = schemas.CompletionParameterSchema(many=True)

    def get(self, api10: str) -> Tuple[Dict, int]:
        api10 = api10[:10]

        if len(api10) != 10:
            msg = f"api10 should have a length of 10. The passed parameter has a length of {len(api10)} ({api10})."  # noqa
            return (
                {"status": msg},
                400,
            )
        result = Registry.completion_calcs(api10s=[api10])
        return {"data": self.schema.dump(result), "status": "success"}, 200


class Completion14(Resource):
    schema = schemas.CompletionParameterSchema(many=True)

    def get(self, api14: str) -> Tuple[Dict, int]:

        if len(api14) != 14:
            msg = f"api14 should have a length of 14. The passed parameter has a length of {len(api14)} ({api14})."  # noqa
            return (
                {"status": msg},
                400,
            )
        result = Registry.completion_calcs(api14s=[api14])
        return {"data": self.schema.dump(result), "status": "success"}, 200


class Completions(Resource):
    schema = schemas.CompletionParameterSchema(many=True)

    def get(self) -> Tuple[Dict, int]:  # type: ignore
        api10 = request.args.get("api10")
        api14 = request.args.get("api14")
        if api10:
            id_var = "api10s"
            ids = [x[:10] for x in api10.split(",")]
        elif api14:
            id_var = "api14s"
            ids = [x[:14] for x in api14.split(",")]
        else:
            return {"status": "missing_argument"}, 400

        result = Registry.completion_calcs(**{id_var: ids})
        return {"data": self.schema.dump(result), "status": "success"}, 200


# class Completion(CompletionResource):
#     """ All data for a completion """

#     schema = schemas.CompletionParameterSchema(many=True)


# class Completions(CompletionListResource):
#     """ All data for a list of completions """

#     schema = schemas.CompletionParameterSchema(many=True)


class Test(Completion10):
    def get(self) -> Tuple[Dict, int]:  # type: ignore
        return request.args, 200


api.add_resource(Test, "/test")
api.add_resource(Completions, "/")
api.add_resource(Completion10, "/api10/<api10>")
api.add_resource(Completion14, "/api14/<api14>")


if __name__ == "__main__":
    from fracfocus import create_app
    from config import get_active_config

    app = create_app()
    app.app_context().push()
    conf = get_active_config()

    api10s = ["4246140916"]
    Registry.completion_calcs(api10s=api10s)
    Registry.query.filter(Registry.api10.in_(api10s)).all()
