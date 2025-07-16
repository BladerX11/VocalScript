import io
import logging
from typing import override

logger = logging.getLogger(__name__)


class StderrToLogger(io.TextIOBase):
    def __init__(self):
        super().__init__()
        self._buffer: str = ""

    @override
    def write(self, msg: str) -> int:
        self._buffer += msg
        if "\n" in self._buffer:
            parts = self._buffer.splitlines(keepends=True)
            for line in parts[:-1]:
                logger.error(line.rstrip("\n"))
            self._buffer = parts[-1]
        return len(msg)

    @override
    def flush(self):
        if self._buffer:
            logger.error(self._buffer.rstrip("\n"))
            self._buffer = ""

    # Optional for loguru
    def stop(self):
        self.flush()

    # Optional for loguru
    async def complete(self):
        self.flush()

