from __future__ import annotations
from typing import Union, List, Dict
import requests
import zipfile
import io
import os
import sys
import logging
from pathlib import Path
import itertools
from timeit import default_timer as timer
import csv
import re

from config import get_active_config
from util import urljoin, hf_size


logger = logging.getLogger(__name__)

conf = get_active_config()


class FileDownloader:
    def __init__(self, url: str):
        self.url = url

    def get(self) -> requests.Response:
        logger.info(f"Starting download from {self.url}...")
        ts = timer()
        r = requests.get(self.url)
        te = timer()
        exc_time = round(te - ts, 0)

        size = self.get_file_size(r)

        logger.info(
            f"Download successful (download size: {hf_size(size or 0)}, download_time: {exc_time}s)",
            extra={"download_bytes": size, "download_seconds": exc_time},
        )
        return r

    def get_file_size(self, r: requests.Response) -> Union[int, None]:
        b = r.headers.get("Content-Length")
        return int(b) if b else None


class ZipDownloader(FileDownloader):
    download_to = conf.COLLECTOR_DOWNLOAD_PATH
    prefix = conf.COLLECTOR_FILE_PREFIX

    def __init__(self, url: str, download_to: str = None, csv_only: bool = True):
        super().__init__(url=url)
        self.download_to = download_to or self.download_to
        self.csv_only = csv_only
        self.filelist: List[zipfile.ZipInfo] = []

    @property
    def paths(self):
        filelist = self._keep_only(self.filelist) if self.csv_only else self.filelist
        result = [Path(os.path.join(self.download_to, x.filename)) for x in filelist]
        result = self.filter_by_prefix(result)
        return self.sort_by_file_no(result)

    @property
    def groups(self) -> Dict[str, List[Path]]:
        groups = itertools.groupby(self.paths, key=lambda f: f.name.split("_")[0])
        return {k: list(g) for k, g in groups}

    def filter_by_prefix(self, filelist: List[Path], prefix: str = None) -> List[Path]:
        prefix = prefix or self.prefix
        return [x for x in filelist if prefix in x.name]

    def unpack(self, r: requests.Response = None) -> ZipDownloader:
        r = r or self.get()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        logger.debug(f"Unpacking zipfile contents to {self.download_to}")
        z.extractall(self.download_to)
        logger.info(f"Unpacked {len(z.filelist)} files")
        self.filelist = z.filelist
        return self

    def _keep_only(
        self, filelist: List[zipfile.ZipInfo], suffix: str = "csv"
    ) -> List[zipfile.ZipInfo]:

        result = [x for x in filelist if x.filename.endswith(suffix)]
        logger.debug(f"Filtered {len(filelist) - len(result)} files")
        return result

    @classmethod
    def from_existing(cls):
        obj = cls(url=None)  # type: ignore
        filelist = [
            os.path.join(cls.download_to, x) for x in os.listdir(cls.download_to)
        ]
        obj.filelist = [zipfile.ZipInfo(filename=f) for f in filelist]
        return obj

    @staticmethod
    def get_file_key(filename: str) -> int:
        result = re.findall(r"\d+", filename)
        n = int(result[0]) if len(result) > 0 else 0
        return n

    def sort_by_file_no(self, filelist: List[Path], reverse: bool = True) -> List[Path]:
        result = list(sorted(filelist, key=lambda x: self.get_file_key(x.name)))
        result = list(reversed(result)) if reverse else result
        return result


if __name__ == "__main__":
    # url = urljoin(conf.COLLECTOR_BASE_URL, conf.COLLECTOR_URL_PATH)
    # d = ZipDownloader(url)
    # r = d.get()
    # d.unpack(r)
    # fp = d.paths[0]
    z = ZipDownloader.from_existing()
    z.paths

