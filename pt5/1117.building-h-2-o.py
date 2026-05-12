from __future__ import annotations

from threading import Barrier, Semaphore
from typing import Callable


class H2O:
    def __init__(self):
        self.hydrogen_slots = Semaphore(2)
        self.oxygen_slots = Semaphore(1)
        self.molecule_barrier = Barrier(3)

    def hydrogen(self, releaseHydrogen: Callable[[], None]) -> None:
        self.hydrogen_slots.acquire()
        releaseHydrogen()
        self.molecule_barrier.wait()
        self.hydrogen_slots.release()

    def oxygen(self, releaseOxygen: Callable[[], None]) -> None:
        self.oxygen_slots.acquire()
        releaseOxygen()
        self.molecule_barrier.wait()
        self.oxygen_slots.release()

