import sys


class Logger:
    """Thin wrapper used while debugging the first CSV parser."""

    def __init__(self, verbose=False, stream=None):
        self.verbose = verbose
        self.stream = stream or sys.stderr

    def info(self, message):
        if self.verbose:
            self._write("INFO", message)

    def debug(self, message):
        if self.verbose:
            self._write("DEBUG", message)

    def _write(self, level, message):
        self.stream.write(f"[{level}] {message}\n")


def get_logger(config, stream=None):
    return Logger(verbose=config.verbose, stream=stream)
