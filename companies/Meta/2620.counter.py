#
# @lc app=leetcode id=2620 lang=python3
#
# [2620] Counter
#
# https://leetcode.com/problems/counter/description/
#
# algorithms
# Easy (82.44%)
# Likes:    1643
# Dislikes: 130
# Total Accepted:    737.1K
# Total Submissions: 894.1K
# Testcase Example:  "10\n[\"call\",\"call\",\"call\"]"
#
# Given an integer n, return a counter function. This counter function initially
# returns n and then returns 1 more than the previous value every subsequent
# time it is called (n, n + 1, n + 2, etc).
#
#
#
# Example 1:
#
# Input:
# n = 10
# ["call","call","call"]
# Output: [10,11,12]
# Explanation:
# counter() = 10 // The first time counter() is called, it returns n.
# counter() = 11 // Returns 1 more than the previous time.
# counter() = 12 // Returns 1 more than the previous time.
#
# Example 2:
#
# Input:
# n = -2
# ["call","call","call","call","call"]
# Output: [-2,-1,0,1,2]
# Explanation: counter() initially returns -2. Then increases after each
# sebsequent call.
#
#
#
# Constraints:
#
#
# -1000^ <= n <= 1000
#
#
# 0 <= calls.length <= 1000
#
#
# calls[i] === "call"
#

# @lc code=start
from typing import Callable


def createCounter(n: int) -> Callable[[], int]:
    """
    Interview explanation:
    Return a counter closure that yields n, then n+1, n+2, ... on each call.

    Algorithm:
    - Capture a mutable current value starting at n.
    - Each invocation returns the current value then increments it.

    Complexity: O(1) time and space per call.
    """
    state = {"value": n}

    def counter() -> int:
        """
        Interview explanation:
        Next value from the counter sequence.

        Algorithm:
        - Read state['value'], increment, return the previous value.

        Complexity: O(1) time and space.
        """
        out = state["value"]
        state["value"] += 1
        return out

    return counter


class Solution:
    def createCounter(self, n: int) -> Callable[[], int]:
        """
        Interview explanation:
        Thin Solution wrapper for createCounter.

        Algorithm:
        - Delegate to createCounter(n).

        Complexity: O(1) to create; O(1) per subsequent call.
        """
        return createCounter(n)
# @lc code=end
