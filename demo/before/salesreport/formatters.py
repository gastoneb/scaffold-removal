import json
from abc import ABC, abstractmethod
from xml.sax.saxutils import escape


class BaseFormatter(ABC):
    @abstractmethod
    def format(self, totals):
        """Return a string for an ordered {region: total} mapping."""


class JsonFormatter(BaseFormatter):
    def format(self, totals):
        return json.dumps(totals, indent=2)


class TextFormatter(BaseFormatter):
    def format(self, totals):
        return "\n".join(f"{region}: {total}" for region, total in totals.items())


class XmlFormatter(BaseFormatter):
    def format(self, totals):
        lines = ["<totals>"]
        for region, total in totals.items():
            lines.append(f'  <region name="{escape(region)}">{total}</region>')
        lines.append("</totals>")
        return "\n".join(lines)


_FORMATTERS = {"json": JsonFormatter, "text": TextFormatter, "xml": XmlFormatter}


def get_formatter(name):
    try:
        return _FORMATTERS[name]()
    except KeyError:
        raise ValueError(f"unknown output format: {name}")
