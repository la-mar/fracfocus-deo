from __future__ import annotations
from typing import Dict, List, Callable, Union, Optional
import logging
from datetime import date, datetime


from collector.parser import Parser
from collector.row_parser import RowParser
from config import get_active_config


conf = get_active_config()

logger = logging.getLogger(__name__)

Scalar = Union[int, float, str, None, datetime, date]
Row = Dict[str, Scalar]


class TransformationError(Exception):
    pass


class Transformer(object):
    parser = RowParser.load_from_config(conf.PARSER_CONFIG)

    def __init__(
        self,
        aliases: Dict[str, str] = None,
        exclude: List[str] = None,
        normalize: bool = False,
        parser: Parser = None,
    ):
        self.normalize = normalize
        self.aliases = aliases or {}
        self.exclude = exclude or []
        self.errors: List[str] = []
        self.parser = parser or self.parser

    def __repr__(self):
        return (
            f"Transformer: {len(self.aliases)} aliases, {len(self.exclude)} exclusions"
        )

    def transform(self, row: dict) -> Row:

        try:
            row = self.drop_exclusions(row)
            row = self.apply_aliases(row)
            row = self.parser.parse(row)

            if "api14" in row.keys():
                row["api14"] = str(row["api14"])
                row["api10"] = row["api14"][:10]

            if len(self.errors) > 0:
                logger.warning(
                    f"Captured {len(self.errors)} parsing errors during transformation: {self.errors}"
                )

            return row
        except Exception as e:
            logger.exception(f"Transformation error: {e}")
            raise TransformationError(e)

    def apply_aliases(self, row: Row) -> Row:
        return {self.aliases[k]: v for k, v in row.items()}

    def drop_exclusions(self, row: Row) -> Row:
        if len(self.exclude) > 0:
            try:
                logger.debug(f"Dropping {len(self.exclude)} columns: {self.exclude}")
                row = {k: v for k, v in row if k not in self.exclude}
            except Exception as e:
                msg = f"Failed attempting to drop columns -- {e}"
                self.errors.append(msg)
                logger.debug(msg)
        return row


if __name__ == "__main__":

    from collector import Endpoint

    ep = Endpoint.load_from_config(conf)["registry"]
    t = Transformer(ep.mappings.aliases, ep.exclude)
    t.transform(row)

