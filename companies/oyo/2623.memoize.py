#
# @lc app=leetcode id=2623 lang=python3
#
# [2623] Memoize
#
# https://leetcode.com/problems/memoize/description/
#
# algorithms
# Medium (65.24%)
# Likes:    779
# Dislikes: 121
# Total Accepted:    192.4K
# Total Submissions: 294.9K
# Testcase Example:  "\"sum\"\n[\"call\",\"call\",\"getCallCount\",\"call\",\"getCallCount\"]\n[[2,2],[2,2],[],[1,2],[]]"
#
# Given a function fn, return a memoized version of that function.
#
# A memoized function is a function that will never be called twice with the
# same inputs. Instead it will return a cached value.
#
# You can assume there are 3 possible input functions: sum, fib, and factorial.
#
#
# sum accepts two integers a and b and returns a + b. Assume that if a value has
# already been cached for the arguments (b, a) where a != b, it cannot be used
# for the arguments (a, b). For example, if the arguments are (3, 2) and (2, 3),
# two separate calls should be made.
#
#
# fib accepts a single integer n and returns 1 if n <= 1 or fib(n - 1) + fib(n -
# 2) otherwise.
#
#
# factorial accepts a single integer n and returns 1 if n <= 1 or factorial(n -
# 1) * n otherwise.
#
#
#
# Example 1:
#
# Input:
# fnName = "sum"
# actions = ["call","call","getCallCount","call","getCallCount"]
# values = [[2,2],[2,2],[],[1,2],[]]
# Output: [4,4,1,3,2]
# Explanation:
# const sum = (a, b) => a + b;
# const memoizedSum = memoize(sum);
# memoizedSum(2, 2); // "call" - returns 4. sum() was called as (2, 2) was not
# seen before.
# memoizedSum(2, 2); // "call" - returns 4. However sum() was not called because
# the same inputs were seen before.
# // "getCallCount" - total call count: 1
# memoizedSum(1, 2); // "call" - returns 3. sum() was called as (1, 2) was not
# seen before.
# // "getCallCount" - total call count: 2
#
# Example 2:
#
# Input:
# fnName = "factorial"
# actions = ["call","call","call","getCallCount","call","getCallCount"]
# values = [[2],[3],[2],[],[3],[]]
# Output: [2,6,2,2,6,2]
# Explanation:
# const factorial = (n) => (n <= 1) ? 1 : (n * factorial(n - 1));
# const memoFactorial = memoize(factorial);
# memoFactorial(2); // "call" - returns 2.
# memoFactorial(3); // "call" - returns 6.
# memoFactorial(2); // "call" - returns 2. However factorial was not called
# because 2 was seen before.
# // "getCallCount" - total call count: 2
# memoFactorial(3); // "call" - returns 6. However factorial was not called
# because 3 was seen before.
# // "getCallCount" - total call count: 2
#
# Example 3:
#
# Input:
# fnName = "fib"
# actions = ["call","getCallCount"]
# values = [[5],[]]
# Output: [8,1]
# Explanation:
# fib(5) = 8 // "call"
# // "getCallCount" - total call count: 1
#
#
#
# Constraints:
#
#
# 0 <= a, b <= 10^5
#
#
# 1 <= n <= 10
#
#
# 1 <= actions.length <= 10^5
#
#
# actions.length === values.length
#
#
# actions[i] is one of "call" and "getCallCount"
#
#
# fnName is one of "sum", "factorial" and "fib"
#

# @lc code=start
from typing import Any, Callable, Dict, Tuple


def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Interview explanation:
    Return a memoized wrapper that caches results by argument tuple.

    Algorithm:
    - On call, look up args in a dict; on miss invoke fn and store the result.
    - Argument order matters: (a,b) and (b,a) are distinct keys.

    Complexity: O(1) amortized per call besides fn; O(k) space for k unique inputs.
    """
    cache: Dict[Tuple[Any, ...], Any] = {}

    def wrapped(*args: Any) -> Any:
        """
        Interview explanation:
        Memoized call for the given arguments.

        Algorithm:
        - Tuple-key lookup; compute and cache on miss.

        Complexity: O(1) amortized cache ops besides fn cost.
        """
        key = args
        if key not in cache:
            cache[key] = fn(*args)
        return cache[key]

    return wrapped


class Solution:
    def memoize(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Interview explanation:
        Thin Solution wrapper for memoize.

        Algorithm:
        - Delegate to memoize(fn).

        Complexity: Same as memoize.
        """
        return memoize(fn)
# @lc code=end
