#
# @lc app=leetcode id=2666 lang=python3
#
# [2666] Allow One Function Call
#
# https://leetcode.com/problems/allow-one-function-call/description/
#
# algorithms
# Easy (86.59%)
# Likes:    597
# Dislikes: 82
# Total Accepted:    202.9K
# Total Submissions: 234.3K
# Testcase Example:  "(a,b,c) => (a + b + c)\n[[1,2,3],[2,3,6]]"
#
# Given a function fn, return a new function that is identical to the original
# function except that it ensures fn is called at most once.
#
#
# The first time the returned function is called, it should return the same
# result as fn.
#
#
# Every subsequent time it is called, it should return undefined.
#
#
#
# Example 1:
#
# Input: fn = (a,b,c) => (a + b + c), calls = [[1,2,3],[2,3,6]]
# Output: [{"calls":1,"value":6}]
# Explanation:
# const onceFn = once(fn);
# onceFn(1, 2, 3); // 6
# onceFn(2, 3, 6); // undefined, fn was not called
#
# Example 2:
#
# Input: fn = (a,b,c) => (a * b * c), calls = [[5,7,4],[2,3,6],[4,6,8]]
# Output: [{"calls":1,"value":140}]
# Explanation:
# const onceFn = once(fn);
# onceFn(5, 7, 4); // 140
# onceFn(2, 3, 6); // undefined, fn was not called
# onceFn(4, 6, 8); // undefined, fn was not called
#
#
#
# Constraints:
#
#
# calls is a valid JSON array
#
#
# 1 <= calls.length <= 10
#
#
# 1 <= calls[i].length <= 100
#
#
# 2 <= JSON.stringify(calls).length <= 1000
#

# @lc code=start

from typing import Any, Callable, Optional


class Solution:
    def once(self, fn: Callable[..., Any]) -> Callable[..., Optional[Any]]:
        """
        Interview explanation:
        JavaScript 30: once(fn) returns a wrapper that calls fn at most once; later calls return None.

        Algorithm:
        - Flag called; on first call invoke fn(*args); afterward return None.

        Complexity: O(1) wrapper overhead plus fn cost.
        """
        called = False
        result: Any = None

        def wrapper(*args: Any) -> Optional[Any]:
            nonlocal called, result
            if called:
                return None
            called = True
            result = fn(*args)
            return result

        return wrapper


def once(fn: Callable[..., Any]) -> Callable[..., Optional[Any]]:
    """
    Interview explanation:
    Top-level LeetCode-style once API.

    Algorithm:
    - Delegate to Solution.once.

    Complexity: O(1) wrapper overhead plus fn cost.
    """
    return Solution().once(fn)
# @lc code=end
