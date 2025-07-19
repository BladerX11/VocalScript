from typing import Callable, Generic, TypeVar

from PySide6.QtCore import QObject, QThread, Signal, Slot

T = TypeVar("T")
_workers: set[QObject] = set()


class TaskWorker(Generic[T], QObject):
    """Worker that runs a function in a separate thread and emits result or error."""

    success: Signal = Signal(object)
    error: Signal = Signal(Exception)
    finished: Signal = Signal()

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
            self.success.emit(result)
        except Exception as e:
            self.error.emit(e)
        finally:
            self.finished.emit()


def dispatch(
    parent: QObject,
    fn: Callable[[], T],
    success_slot: Callable[[T], None] | None = None,
    error_slot: Callable[[Exception], None] | None = None,
    finished_slot: Callable[[], None] | None = None,
):
    """Helper to run a function in a background QThread.

    Parameters:
        parent (QObject): Parent for the QThread to ensure proper QObject hierarchy.
        fn (callable): The function to execute in the background thread.
        success_slot (callable, optional): Slot to connect to the worker's success signal.
        error_slot (callable, optional): Slot to connect to the worker's error signal.
        finished_slot (callable, optional): Slot to connect to the worker's finished signal.
    """
    thread = QThread(parent)
    worker = TaskWorker(fn)
    _workers.add(worker)
    _ = worker.moveToThread(thread)

    if error_slot:
        _ = worker.error.connect(error_slot)
    else:

        def raise_error(e: Exception):
            raise e

        _ = worker.error.connect(raise_error)

    if success_slot:
        _ = worker.success.connect(success_slot)

    if finished_slot:
        _ = worker.finished.connect(finished_slot)

    _ = thread.started.connect(worker.run)
    _ = worker.finished.connect(thread.quit)
    _ = worker.finished.connect(lambda: _workers.remove(worker))
    _ = worker.finished.connect(worker.deleteLater)
    _ = thread.finished.connect(thread.deleteLater)
    thread.start()
