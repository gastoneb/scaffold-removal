import os
from dataclasses import dataclass


@dataclass
class Config:
    """Settings added while experimenting; only the defaults are ever used."""

    input_format: str = "csv"
    output_format: str = "json"
    verbose: bool = False
    debug_dump: bool = False
    sort_by: str = "region"
    decimals: int = 2

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        return cls(
            input_format=env.get("SALESREPORT_INPUT", cls.input_format),
            output_format=env.get("SALESREPORT_OUTPUT", cls.output_format),
            verbose=env.get("SALESREPORT_VERBOSE", "") == "1",
            debug_dump=env.get("SALESREPORT_DEBUG", "") == "1",
            sort_by=env.get("SALESREPORT_SORT", cls.sort_by),
            decimals=int(env.get("SALESREPORT_DECIMALS", cls.decimals)),
        )
