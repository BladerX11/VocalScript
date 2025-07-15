from typing import Callable, Generic, TypeVar

from PySide6.QtCore import QObject, QThread, Signal, Slot

T = TypeVar("T")
_workers: set[QObject] = set()


class TaskWorker(Generic[T], QObject):
    """Worker that runs a function in a separate thread and emits result or error."""

    finished: Signal = Signal(object)
    error: Signal = Signal(Exception)

    def __init__(self, fn: Callable[[], T]):
        """Initialize the worker with a function and its arguments.

        Args:
            parent (QObject): Parent QObject for the worker.
            fn (Callable): The function to run in the background thread.
        """
        super().__init__()
        self.fn: Callable[[], T] = fn

    @Slot()
    def run(self) -> None:
        try:
            result: T = self.fn()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


def dispatch(
    parent: QObject,
    fn: Callable[[], T],
    finished_slot: Callable[[T], None] | None = None,
    error_slot: Callable[[Exception], None] | None = None,
):
    """Helper to run a function in a background QThread.

    Parameters:
        parent (QObject): Parent for the QThread to ensure proper QObject hierarchy.
        fn (callable): The function to execute in the background thread.
        finished_slot (callable, optional): Slot to connect to the worker's finished signal.
        error_slot (callable, optional): Slot to connect to the worker's error signal.
    """
    thread = QThread(parent)
    worker = TaskWorker(fn)
    _workers.add(worker)
    _ = worker.moveToThread(thread)

    if error_slot:
        worker.error.connect(error_slot)
    else:

        def raise_error(e: Exception):
            raise e

        worker.error.connect(raise_error)

    if finished_slot:
        _ = worker.finished.connect(finished_slot)

    _ = thread.started.connect(worker.run)
    _ = worker.finished.connect(thread.quit)
    _ = worker.error.connect(thread.quit)
    _ = worker.finished.connect(lambda _: _workers.remove(worker))
    _ = worker.error.connect(lambda _: _workers.remove(worker))
    _ = worker.finished.connect(worker.deleteLater)
    _ = worker.error.connect(worker.deleteLater)
    _ = thread.finished.connect(thread.deleteLater)
    thread.start()
