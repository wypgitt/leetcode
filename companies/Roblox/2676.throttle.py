#
# @lc app=leetcode id=2676 lang=python3
#
# [2676] Throttle
#
# https://leetcode.com/problems/throttle/description/
#
# algorithms
# Medium (83.40%)
# Likes:    171
# Dislikes: 30
# Total Accepted:    11.8K
# Total Submissions: 14.2K
# Testcase Example:  "100\n[{\"t\":20,\"inputs\":[1]}]"
#
#
# Given a function fn and a time in milliseconds t, return a throttled
# version of that function.
#
# A throttled function is first called without delay and then, for a time
# interval of t milliseconds, can't be executed but should store the
# latest function arguments provided to call fn with them after the end of
# the delay.
#
# For instance, t = 50ms, and the function was called at 30ms, 40ms, and
# 60ms.
#
# At 30ms, without delay, the throttled function fn should be called with
# the arguments, and calling the throttled function fn should be blocked
# for the following t milliseconds.
#
# At 40ms, the function should just save arguments.
#
# At 60ms, arguments should overwrite currently stored arguments from the
# second call because the second and third calls are made before 80ms.
# Once the delay has passed, the throttled function fn should be called
# with the latest arguments provided during the delay period, and it
# should also create another delay period of 80ms + t.
#
# The above diagram shows how throttle will transform events. Each
# rectangle represents 100ms and the throttle time is 400ms. Each color
# represents a different set of inputs.
#
# Example 1:
#
# Input:
# t = 100,
# calls = [
#   {"t":20,"inputs":[1]}
# ]
# Output: [{"t":20,"inputs":[1]}]
# Explanation: The 1st call is always called without delay
#
# Example 2:
#
# Input:
# t = 50,
# calls = [
#   {"t":50,"inputs":[1]},
#   {"t":75,"inputs":[2]}
# ]
# Output: [{"t":50,"inputs":[1]},{"t":100,"inputs":[2]}]
# Explanation:
# The 1st is called a function with arguments (1) without delay.
# The 2nd is called at 75ms, within the delay period because 50ms + 50ms =
# 100ms, so the next call can be reached at 100ms. Therefore, we save
# arguments from the 2nd call to use them at the callback of the 1st call.
#
# Example 3:
#
# Input:
# t = 70,
# calls = [
#   {"t":50,"inputs":[1]},
#   {"t":75,"inputs":[2]},
#   {"t":90,"inputs":[8]},
#   {"t": 140, "inputs":[5,7]},
#   {"t": 300, "inputs": [9,4]}
# ]
# Output:
# [{"t":50,"inputs":[1]},{"t":120,"inputs":[8]},{"t":190,"inputs":[5,7]},{"t":300,"inputs":[9,4]}]
# Explanation:
# The 1st is called a function with arguments (1) without delay.
# The 2nd is called at 75ms within the delay period because 50ms + 70ms =
# 120ms, so it should only save arguments.
# The 3rd is also called within the delay period, and because we need just
# the latest function arguments, we overwrite previous ones. After the
# delay period, we do a callback at 120ms with saved arguments. That
# callback makes another delay period of 120ms + 70ms = 190ms so that the
# next function can be called at 190ms.
# The 4th is called at 140ms in the delay period, so it should be called
# as a callback at 190ms. That will create another delay period of 190ms +
# 70ms = 260ms.
# The 5th is called at 300ms, but it is after 260ms, so it should be
# called immediately and should create another delay period of 300ms +
# 70ms = 370ms.
#
# Constraints:
#
# 0 <= t <= 1000
#
# 1 <= calls.length <= 10
#
# 0 <= calls[i].t <= 1000
#
# 0 <= calls[i].inputs[j], calls[i].inputs.length <= 10
#
# @lc code=start

from typing import Any, Callable, List, Optional


class Solution:
    def throttle(self, fn: Callable[..., Any], t: int) -> Callable[..., Any]:
        """
        Interview explanation:
        JavaScript 30: throttle(fn, t) — invoke fn at most once per t ms. Leading call runs
        immediately; if calls arrive during cooldown, the latest args run when cooldown ends.

        Algorithm:
        - Track next_allowed time and pending args. On call: if now >= next_allowed run now;
          else schedule/overwrite pending for next_allowed. Python simulation uses a logical clock
          via optional `_now` kw for tests; default uses time.time()*1000.

        Complexity: O(1) per call overhead.
        """
        import time

        next_allowed = 0.0
        pending: Optional[List[Any]] = None
        timer_at: Optional[float] = None

        def run(args: List[Any], now: float) -> None:
            nonlocal next_allowed, pending, timer_at
            fn(*args)
            next_allowed = now + t
            pending = None
            timer_at = None

        def wrapped(*args: Any, _now: Optional[float] = None) -> None:
            nonlocal next_allowed, pending, timer_at
            now = time.time() * 1000 if _now is None else _now
            if now >= next_allowed:
                run(list(args), now)
            else:
                pending = list(args)
                timer_at = next_allowed
                # In a real event loop we'd setTimeout; here expose flush for simulation.
                wrapped._pending_until = timer_at  # type: ignore[attr-defined]

        def flush(_now: Optional[float] = None) -> None:
            nonlocal pending
            if pending is None:
                return
            now = time.time() * 1000 if _now is None else _now
            if now >= next_allowed:
                run(pending, now)

        wrapped.flush = flush  # type: ignore[attr-defined]
        return wrapped


def throttle(fn: Callable[..., Any], t: int) -> Callable[..., Any]:
    """
    Interview explanation:
    Top-level LeetCode-style throttle API.

    Algorithm:
    - Delegate to Solution.throttle.

    Complexity: O(1) per call overhead.
    """
    return Solution().throttle(fn, t)
# @lc code=end
