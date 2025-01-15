from __future__ import annotations

import collections
from asyncio import Future, Lock


class BetterLock(Lock):
    async def wait(self) -> None:
        if not self.locked():
            return

        if self._waiters is None:
            self._waiters = collections.deque()

        fut = Future()
        self._waiters.append(fut)
        try:
            await fut
        finally:
            self._waiters.remove(fut)
