#
# @lc app=leetcode id=2632 lang=python3
#
# [2632] Curry
#
# https://leetcode.com/problems/curry/description/
#
# algorithms
# Medium (89.45%)
# Likes:    349
# Dislikes: 35
# Total Accepted:    19.1K
# Total Submissions: 21.3K
# Testcase Example:  "function sum(a, b, c) { return a + b + c; }\n[[1],[2],[3]]"
#
#
# Given a function fn, return a curried version of that function.
#
# A curried function is a function that accepts fewer or an equal number
# of parameters as the original function and returns either another
# curried function or the same value the original function would have
# returned.
#
# In practical terms, if you called the original function like sum(1,2,3),
# you would call the curried version like csum(1)(2)(3), csum(1)(2,3),
# csum(1,2)(3), or csum(1,2,3). All these methods of calling the curried
# function should return the same value as the original.
#
# Example 1:
#
# Input:
# fn = function sum(a, b, c) { return a + b + c; }
# inputs = [[1],[2],[3]]
# Output: 6
# Explanation:
# The code being executed is:
# const curriedSum = curry(fn);
# curriedSum(1)(2)(3) === 6;
# curriedSum(1)(2)(3) should return the same value as sum(1, 2, 3).
#
# Example 2:
#
# Input:
# fn = function sum(a, b, c) { return a + b + c; }
# inputs = [[1,2],[3]]
# Output: 6
# Explanation:
# curriedSum(1, 2)(3) should return the same value as sum(1, 2, 3).
#
# Example 3:
#
# Input:
# fn = function sum(a, b, c) { return a + b + c; }
# inputs = [[],[],[1,2,3]]
# Output: 6
# Explanation:
# You should be able to pass the parameters in any way, including all at
# once or none at all.
# curriedSum()()(1, 2, 3) should return the same value as sum(1, 2, 3).
#
# Example 4:
#
# Input:
# fn = function life() { return 42; }
# inputs = [[]]
# Output: 42
# Explanation:
# currying a function that accepts zero parameters should effectively do
# nothing.
# curriedLife() === 42
#
# Constraints:
#
# 1 <= inputs.length <= 1000
#
# 0 <= inputs[i][j] <= 10^5
#
# 0 <= fn.length <= 1000
#
# inputs.flat().length == fn.length
#
# function parameters explicitly defined
#
# If fn.length > 0 then the last array in inputs is not empty
#
# If fn.length === 0 then inputs.length === 1
#
# @lc code=start
from typing import Any, Callable


def curry(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Interview explanation:
    Curry fn so arguments may be supplied across multiple calls until
    fn's declared arity (co_argcount) is reached, then invoke fn.

    Algorithm:
    - Return a nested accumulator that appends args; when len(args) >=
      arity, call fn(*args[:arity]); else return another accumulator.

    Complexity: O(arity) to complete a full application; O(arity) space.
    """
    arity = fn.__code__.co_argcount

    def curried(*args: Any) -> Any:
        """
        Interview explanation:
        Accumulate args or evaluate when enough are present.

        Algorithm:
        - If enough args, call fn; else return a closure capturing them.

        Complexity: O(1) per partial call; O(arity) on final call.
        """
        if len(args) >= arity:
            return fn(*args[:arity])

        def next_partial(*more: Any) -> Any:
            """
            Interview explanation:
            Continue currying with additional arguments.

            Algorithm:
            - Concatenate prior and new args and recurse into curried.

            Complexity: O(k) to concatenate k args so far.
            """
            return curried(*(args + more))

        return next_partial

    return curried


class Solution:
    def curry(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Interview explanation:
        Thin Solution wrapper for curry.

        Algorithm:
        - Delegate to curry(fn).

        Complexity: Same as curry.
        """
        return curry(fn)
# @lc code=end
