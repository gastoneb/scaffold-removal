import csv
import json
from abc import ABC, abstractmethod


class BaseReader(ABC):
    @abstractmethod
    def read(self, path):
        """Return a list of {"region": str, "amount": float} rows."""


class CsvReader(BaseReader):
    def read(self, path):
        rows = []
        with open(path, newline="", encoding="utf-8-sig") as handle:  # Excel exports add a BOM
            for number, record in enumerate(csv.DictReader(handle), start=2):
                rows.append(self._parse(record, number))
        return rows

    @staticmethod
    def _parse(record, number):
        region = (record.get("region") or "").strip()
        if not region:
            raise ValueError(f"line {number}: missing region")
        try:
            amount = float(record.get("amount"))
        except (TypeError, ValueError):
            raise ValueError(f"line {number}: invalid amount {record.get('amount')!r}")
        return {"region": region, "amount": amount}


class JsonReader(BaseReader):
    """Experimental: the first prototype read JSON. Nothing produces it any more."""

    def read(self, path):
        with open(path) as handle:
            return [
                {"region": item["region"], "amount": float(item["amount"])}
                for item in json.load(handle)
            ]


_READERS = {"csv": CsvReader, "json": JsonReader}


def get_reader(name):
    try:
        return _READERS[name]()
    except KeyError:
        raise ValueError(f"unknown input format: {name}")
