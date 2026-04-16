import os
import sys
import time


LOG_FILE = "app.log"
MAX_BYTES = 64 * 1024

_writer = None
_loggers = {}


def getLogger(name="root"):
    if name not in _loggers:
        _loggers[name] = _Logger(name)
    return _loggers[name]


class _Logger:
    def __init__(self, name):
        self.name = name

    def log(self, message):
        _get_writer().write(self.name, "INFO", message)

    def debug(self, message):
        _get_writer().write(self.name, "DEBUG", message)

    def info(self, message):
        _get_writer().write(self.name, "INFO", message)

    def warning(self, message):
        _get_writer().write(self.name, "WARNING", message)

    def error(self, message):
        _get_writer().write(self.name, "ERROR", message)

    def exception(self, message, exception=None):
        _get_writer().write_exception(self.name, "ERROR", message, exception)


class _LogWriter:
    def __init__(self, filename, max_bytes):
        self.filename = filename
        self.rotated_filename = filename + ".1"
        self.max_bytes = max_bytes

    def write(self, source, level, message):
        line = f"[{self._datetime()}] [{level}] [{source}] {message}"
        print(line)
        self._write_file(line)

    def write_exception(self, source, level, message, exception=None):
        self.write(source, level, message)
        for line in self._format_exception(exception):
            self.write(source, level, line)

    def _write_file(self, line):
        try:
            self._rotate_if_needed(len(line) + 1)
            with open(self.filename, "a") as f:
                f.write(line + "\n")
        except OSError as e:
            print("Logging error:", e)

    def _rotate_if_needed(self, incoming_bytes):
        try:
            current_size = os.stat(self.filename)[6]
        except OSError:
            return

        if current_size + incoming_bytes <= self.max_bytes:
            return

        try:
            os.remove(self.rotated_filename)
        except OSError:
            pass

        try:
            os.rename(self.filename, self.rotated_filename)
        except OSError:
            pass

    def _datetime(self):
        now = time.localtime()
        return (
            f"{now[0]:04d}-{now[1]:02d}-{now[2]:02d} "
            f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}"
        )

    def _format_exception(self, exception=None):
        exc_info = None
        if exception is None:
            try:
                exc_info = sys.exc_info()
                exception = exc_info[1]
            except AttributeError:
                pass

        if exception is None:
            return []

        try:
            import io

            output = io.StringIO()
            sys.print_exception(exception, output)
            return output.getvalue().splitlines()
        except Exception:
            pass

        try:
            import traceback

            if exc_info is None:
                exc_info = sys.exc_info()

            return [
                line.rstrip("\n")
                for line in traceback.format_exception(*exc_info)
            ]
        except Exception:
            return [repr(exception)]


def _get_writer():
    global _writer
    if _writer is None:
        _writer = _LogWriter(LOG_FILE, MAX_BYTES)
    return _writer
