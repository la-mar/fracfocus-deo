# import pytest  # pylint: disable=unused-import

# from collector.endpoint import Endpoint

# # pylint: disable=missing-function-docstring,missing-module-docstring,no-self-use


# class TestEndpoint:
#     def test_endpoint_repr(self, endpoint):
#         repr(endpoint)

#     def test_endpoint_iter(self, endpoint):
#         d = dict(endpoint)
#         assert isinstance(d, dict)
#         assert len(d.keys()) > 0

#     def test_load_from_config(self, conf):
#         Endpoint.load_from_config(conf)

#     def test_load_from_empty_config(self):
#         with pytest.raises(AttributeError):
#             assert Endpoint.load_from_config({}) == {}

#     def test_load_from_config_bad_endpoint(self):
#         class Conf:
#             endpoints = {None: None}

#         Endpoint.load_from_config(Conf())

#     def test_locate_model_from_globals(self, endpoint):
#         assert endpoint.locate_model("pytest")

#     def test_locate_model_not_found(self, endpoint):
#         with pytest.raises(ModuleNotFoundError):
#             endpoint.locate_model("not_a_real_model")

