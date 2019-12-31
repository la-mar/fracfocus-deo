from __future__ import annotations
from typing import Callable, Dict, List, Union  # pylint: disable=unused-import

import logging
from config import get_active_config

import util

from collector.parser import Parser

conf = get_active_config()

sp = util.StringProcessor()

logger = logging.getLogger(__name__)


class RowParser(object):
    """ Transform an XML response into a normalized Python object"""

    def __init__(
        self,
        aliases: Dict[str, str] = None,
        exclude: List[str] = None,
        normalize: bool = False,
        parsers: List[Parser] = None,
    ):
        self.normalize = normalize
        self.aliases = aliases or {}
        self.exclude = exclude or []
        self.parsers = parsers or []
        self.errors: List[str] = []

    def __repr__(self):
        s = "s" if len(self.parsers) > 1 else ""
        return f"RowParser: {len(self.parsers)} attached parser{s}"

    def add_parser(
        self, parser: Parser = None, ruleset: Dict[str, List] = None, name: str = None
    ):
        self.parsers.append(parser or Parser.init(ruleset, name=name))
        return self

    def normalize_keys(self, data: Dict) -> Dict:
        return util.apply_transformation(data, sp.normalize, keys=True, values=False)

    def parse_value_dtypes(self, data: Dict) -> Dict:
        for parser in self.parsers:
            data = util.apply_transformation(
                data, parser.parse, keys=False, values=True
            )
        return data

    def parse(self, row: dict, parse_dtypes: bool = True, **kwargs) -> Dict:
        # parsed = self.normalize_keys(row)
        if parse_dtypes:
            parsed = self.parse_value_dtypes(row)
        return parsed

    @staticmethod
    def load_from_config(parser_conf: dict):
        parser_conf = parser_conf.get("parsers", parser_conf)
        parsers: List[Parser] = []
        for name, parser_def in parser_conf.items():
            ruleset = parser_def.get("rules", parser_def)
            parsers.append(Parser.init(ruleset, name))

        return RowParser(parsers=parsers)


if __name__ == "__main__":
    rp = RowParser.load_from_config(conf.PARSER_CONFIG)
    rp.parse(row)
