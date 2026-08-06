#
# @lc app=leetcode id=2650 lang=python3
#
# [2650] Design Cancellable Function
#
# https://leetcode.com/problems/design-cancellable-function/description/
#
# algorithms
# Hard (57.88%)
# Likes:    73
# Dislikes: 21
# Total Accepted:    5.4K
# Total Submissions: 9.3K
# Testcase Example:  "function*() { return 42; }\n{\"cancelledAt\":100}"
#
# Sometimes you have a long running task, and you may wish to cancel it before
# it completes. To help with this goal, write a function cancellable that
# accepts a generator object and returns an array of two values: a cancel
# function and a promise.
#
# You may assume the generator function will only yield promises. It is your
# function's responsibility to pass the values resolved by the promise back to
# the generator. If the promise rejects, your function should throw that error
# back to the generator.
#
# If the cancel callback is called before the generator is done, your function
# should throw an error back to the generator. That error should be the
# string "Cancelled" (Not an Error object). If the error was caught, the
# returned promise should resolve with the next value that was yielded or
# returned. Otherwise, the promise should reject with the thrown error. No more
# code should be executed.
#
# When the generator is done, the promise your function returned should resolve
# the value the generator returned. If, however, the generator throws an error,
# the returned promise should reject with the error.
#
# An example of how your code would be used:
#
# function* tasks() {
#   const val = yield new Promise(resolve => resolve(2 + 2));
#   yield new Promise(resolve => setTimeout(resolve, 100));
#   return val + 1; // calculation shouldn't be done.
# }
# const [cancel, promise] = cancellable(tasks());
# setTimeout(cancel, 50);
# promise.catch(console.log); // logs "Cancelled" at t=50ms
#
# If instead cancel() was not called or was called after t=100ms, the promise
# would have resolved 5.
#
#
#
# Example 1:
#
# Input:
# generatorFunction = function*() {
#   return 42;
# }
# cancelledAt = 100
# Output: {"resolved": 42}
# Explanation:
# const generator = generatorFunction();
# const [cancel, promise] = cancellable(generator);
# setTimeout(cancel, 100);
# promise.then(console.log); // resolves 42 at t=0ms
#
# The generator immediately yields 42 and finishes. Because of that, the
# returned promise immediately resolves 42. Note that cancelling a finished
# generator does nothing.
#
# Example 2:
#
# Input:
# generatorFunction = function*() {
#   const msg = yield new Promise(res => res("Hello"));
#   throw `Error: ${msg}`;
# }
# cancelledAt = null
# Output: {"rejected": "Error: Hello"}
# Explanation:
# A promise is yielded. The function handles this by waiting for it to resolve
# and then passes the resolved value back to the generator. Then an error is
# thrown which has the effect of causing the promise to reject with the same
# thrown error.
#
# Example 3:
#
# Input:
# generatorFunction = function*() {
#   yield new Promise(res => setTimeout(res, 200));
#   return "Success";
# }
# cancelledAt = 100
# Output: {"rejected": "Cancelled"}
# Explanation:
# While the function is waiting for the yielded promise to resolve, cancel() is
# called. This causes an error message to be sent back to the generator. Since
# this error is uncaught, the returned promise rejected with this error.
#
# Example 4:
#
# Input:
# generatorFunction = function*() {
#   let result = 0;
#   yield new Promise(res => setTimeout(res, 100));
#   result += yield new Promise(res => res(1));
#   yield new Promise(res => setTimeout(res, 100));
#   result += yield new Promise(res => res(1));
#   return result;
# }
# cancelledAt = null
# Output: {"resolved": 2}
# Explanation:
# 4 promises are yielded. Two of those promises have their values added to the
# result. After 200ms, the generator finishes with a value of 2, and that value
# is resolved by the returned promise.
#
# Example 5:
#
# Input:
# generatorFunction = function*() {
#   let result = 0;
#   try {
#     yield new Promise(res => setTimeout(res, 100));
#     result += yield new Promise(res => res(1));
#     yield new Promise(res => setTimeout(res, 100));
#     result += yield new Promise(res => res(1));
#   } catch(e) {
#     return result;
#   }
#   return result;
# }
# cancelledAt = 150
# Output: {"resolved": 1}
# Explanation:
# The first two yielded promises resolve and cause the result to increment.
# However, at t=150ms, the generator is cancelled. The error sent to the
# generator is caught and the result is returned and finally resolved by the
# returned promise.
#
# Example 6:
#
# Input:
# generatorFunction = function*() {
#   try {
#     yield new Promise((resolve, reject) => reject("Promise Rejected"));
#   } catch(e) {
#     let a = yield new Promise(resolve => resolve(2));
#     let b = yield new Promise(resolve => resolve(2));
#     return a + b;
#   };
# }
# cancelledAt = null
# Output: {"resolved": 4}
# Explanation:
# The first yielded promise immediately rejects. This error is caught. Because
# the generator hasn't been cancelled, execution continues as usual. It ends up
# resolving 2 + 2 = 4.
#
#
#
# Constraints:
#
#
# cancelledAt == null or 0 <= cancelledAt <= 1000
#
#
# generatorFunction returns a generator object
#

# @lc code=start
import asyncio
from typing import Any, Awaitable, Callable, Generator, Tuple


class _Cancelled(Exception):
    """
    Interview explanation:
    Stand-in for JS throwing the bare string "Cancelled" into the generator.
    Catch handlers can inspect args/str to mirror JS catch(e) with e ===
    "Cancelled".

    Algorithm:
    - Exception whose message/args carry "Cancelled".

    Complexity: O(1).
    """


def cancellable(
    generator: Generator[Awaitable[Any], Any, Any],
) -> Tuple[Callable[[], None], Awaitable[Any]]:
    """
    Interview explanation:
    JS cancellable(generator) port. Synchronously returns (cancel, promise)
    where promise is an awaitable that drives a generator yielding awaitables:
    send resolved values, throw rejections, and on cancel throw "Cancelled"
    (here as _Cancelled("Cancelled")) into the generator. If that is caught,
    continue; else the promise rejects. When the generator finishes, resolve
    with its return value.

    Algorithm:
    - Shared cancel flag checked while awaiting each yielded future (race
      against cancel via wait).
    - cancel() sets the flag; finished generators ignore further cancels.
    - Drive with next/send/throw until StopIteration.

    Complexity: O(steps) awaits; O(1) extra space besides tasks.
    """
    state = {"cancelled": False, "done": False}

    def cancel() -> None:
        """
        Interview explanation:
        Request cancellation before the generator completes (JS cancel()).

        Algorithm:
        - Set cancelled flag if not already done.

        Complexity: O(1).
        """
        if not state["done"]:
            state["cancelled"] = True

    async def run() -> Any:
        """
        Interview explanation:
        Async driver that acts as the returned JS promise body.

        Algorithm:
        - Obtain first yield via next(); then loop: race awaitable vs cancel,
          send values or throw errors/cancel into the generator.

        Complexity: Proportional to generator steps and await durations.
        """
        try:
            try:
                nxt = next(generator)
            except StopIteration as e:
                return e.value

            while True:
                if state["cancelled"]:
                    try:
                        nxt = generator.throw(_Cancelled("Cancelled"))
                    except StopIteration as e:
                        return e.value
                    continue

                task = asyncio.ensure_future(nxt)

                async def _wait_cancel() -> None:
                    """
                    Interview explanation:
                    Poll until cancel is requested, then complete.

                    Algorithm:
                    - Busy-wait with short sleeps so we can race without a loop.

                    Complexity: O(wait time / poll interval).
                    """
                    while not state["cancelled"]:
                        await asyncio.sleep(0.001)
                        if task.done():
                            return

                cancel_task = asyncio.create_task(_wait_cancel())
                try:
                    done, _pending = await asyncio.wait(
                        {task, cancel_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if state["cancelled"] and not task.done():
                        task.cancel()
                        try:
                            await task
                        except (asyncio.CancelledError, Exception):
                            # Swallow cancel/errors from the abandoned awaitable.
                            _ = None
                        try:
                            nxt = generator.throw(_Cancelled("Cancelled"))
                        except StopIteration as e:
                            return e.value
                        continue

                    try:
                        value = task.result()
                    except Exception as err:
                        try:
                            nxt = generator.throw(type(err), err, err.__traceback__)
                        except StopIteration as e:
                            return e.value
                        continue

                    try:
                        nxt = generator.send(value)
                    except StopIteration as e:
                        return e.value
                finally:
                    if not cancel_task.done():
                        cancel_task.cancel()
                        try:
                            await cancel_task
                        except asyncio.CancelledError:
                            _ = None
        finally:
            state["done"] = True

    return cancel, run()


class Solution:
    def cancellable(
        self, generator: Generator[Awaitable[Any], Any, Any]
    ) -> Tuple[Callable[[], None], Awaitable[Any]]:
        """
        Interview explanation:
        Thin Solution wrapper for cancellable.

        Algorithm:
        - Delegate to cancellable(generator).

        Complexity: Same as cancellable.
        """
        return cancellable(generator)
# @lc code=end
