import sys

from .aggregate import aggregate
from .config import Config
from .formatters import get_formatter
from .logging_utils import get_logger
from .readers import get_reader


def main(argv=None, env=None, stdout=None, stderr=None):
    argv = sys.argv[1:] if argv is None else argv
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    if len(argv) != 1:
        stderr.write("usage: python -m salesreport FILE\n")
        return 2

    config = Config.from_env(env)
    logger = get_logger(config, stderr)
    try:
        logger.info(f"reading {argv[0]} as {config.input_format}")
        rows = get_reader(config.input_format).read(argv[0])
        logger.debug(f"read {len(rows)} rows")
        if config.debug_dump:
            logger.debug(f"rows: {rows}")
        totals = aggregate(rows, config.sort_by, config.decimals)
        stdout.write(get_formatter(config.output_format).format(totals) + "\n")
    except (OSError, ValueError) as error:
        stderr.write(f"error: {error}\n")
        return 1
    return 0
