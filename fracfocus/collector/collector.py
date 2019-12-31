from __future__ import annotations
from typing import Dict, List, Union, Any
import logging
from datetime import datetime
import csv
from pathlib import Path

from flask_sqlalchemy import Model
import requests


from api.models import *
from collector.endpoint import Endpoint
from collector.transformer import Transformer
from config import get_active_config
from collector.util import retry

logger = logging.getLogger(__name__)

conf = get_active_config()


class Collector(object):
    """ Acts as the conduit for transferring newly collected data into a backend data model """

    _tf = None
    _endpoint = None
    _functions = None
    _model = None

    def __init__(
        self,
        endpoint: Endpoint,
        functions: Dict[Union[str, None], Union[str, None]] = None,
    ):
        self.endpoint = endpoint
        self._functions = functions

    @property
    def functions(self):
        if self._functions is None:
            self._functions = conf.functions
        return self._functions

    @property
    def model(self):
        if self._model is None:
            self._model = self.endpoint.model
        return self._model

    @property
    def tf(self):
        if self._tf is None:
            self._tf = Transformer(
                aliases=self.endpoint.mappings.get("aliases", {}),
                exclude=self.endpoint.exclude,
            )
        return self._tf

    def transform(self, data: dict) -> dict:
        return self.tf.transform(data)


class FracFocusCollector(Collector):
    def collect(
        self,
        filelist: Union[Path, List[Path]],
        update_on_conflict: bool = True,
        ignore_on_conflict: bool = False,
    ):
        if not isinstance(filelist, list):
            filelist = [filelist]

        for path in filelist:
            logger.info(f"Collecting file {path}")
            with open(path) as f:
                csvreader = csv.DictReader(f)
                rows = []
                for idx, row in enumerate(csvreader):
                    transformed = self.transform(row)
                    rows.append(transformed)

                    if idx % conf.COLLECTOR_WRITE_SIZE == 0:
                        self.model.core_insert(
                            rows,
                            update_on_conflict=update_on_conflict,
                            ignore_on_conflict=ignore_on_conflict,
                        )
                        rows = []

                # persist leftovers
                self.model.core_insert(rows)


if __name__ == "__main__":
    from fracfocus import create_app, db
    from collector import Endpoint
    import requests
    from pathlib import Path
    import os

    app = create_app()
    app.app_context().push()

    endpoints = Endpoint.load_from_config(conf)

    endpoint = endpoints["registry"]
    c = FracFocusCollector(endpoint)

    paths = [
        Path(os.path.join(conf.COLLECTOR_DOWNLOAD_PATH, x))
        for x in os.listdir(conf.COLLECTOR_DOWNLOAD_PATH)
    ]

    paths

    row = {
        "upload_key": "68acaa3e-c788-45fb-8f08-b1dc81ccf0ca",
        "api14": "42127380120000",
        "state_no": 42,
        "county_no": 127,
        "operator": "Freedom Production, Inc.",
        "well_name": "KATHERINE BROWN UNIT 2H",
        "lat": 28.439819444,
        "lon": -99.798308333,
        "proj": "NAD27",
        "tvd": 6752,
        "total_base_water_volume": 7469522,
        "total_base_non_water_volume": 0,
        "state": "Texas",
        "county": "Dimmit",
        "ff_version": 3,
        "is_federal_well": False,
        "is_indian_well": False,
        "source": None,
        "dtmod": None,
        "purpose_key": None,
        "trade_name": "NA",
        "supplier": "NA",
        "purpose": "N/A",
        "system_approach": None,
        "is_water": None,
        "purpose_percent_hf_job": None,
        "purpose_ingredient_msds": None,
        "ingredient_key": None,
        "ingredient_name": "Poly(oxy-1,2-ethanediyl),.alpha.-(4-nonylphenyl)-.omega.-hydroxy, branched",
        "cas_number": "127087-87-0",
        "percent_high_additive": 0.00484,
        "percent_hf_job": 0.00094,
        "ingredient_comment": None,
        "ingredient_msds": False,
        "ingredient_mass": 0,
        "claimant_company": None,
        "disclosure_key": "68acaa3e-c788-45fb-8f08-b1dc81ccf0ca",
        "api10": "4212738012",
    }
