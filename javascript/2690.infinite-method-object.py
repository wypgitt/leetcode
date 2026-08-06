#
# @lc app=leetcode id=2690 lang=python3
#
# [2690] Infinite Method Object
#
# https://leetcode.com/problems/infinite-method-object/description/
#
# algorithms
# Easy (93.07%)
# Likes:    32
# Dislikes: 9
# Total Accepted:    2.2K
# Total Submissions: 2.4K
# Testcase Example:  "\"abc123\""
#
#
# Write a function that returns an infinite-method object.
#
# An infinite-method object is defined as an object that allows you to
# call any method and it will always return the name of the method.
#
# For example, if you execute obj.abc123(), it will return "abc123".
#
# Example 1:
#
# Input: method = "abc123"
# Output: "abc123"
# Explanation:
# const obj = createInfiniteObject();
# obj['abc123'](); // "abc123"
# The returned string should always match the method name.
#
# Example 2:
#
# Input: method = ".-qw73n|^2It"
# Output: ".-qw73n|^2It"
# Explanation: The returned string should always match the method name.
#
# Constraints:
#
# 0 <= method.length <= 1000
#
# @lc code=start

from typing import Any, Callable


class _Infinite:
    def __getattr__(self, name: str) -> Callable[..., str]:
        def method(*args: Any) -> str:
            return name

        return method


class Solution:
    def createInfiniteObject(self) -> Any:
        """
        Interview explanation:
        JavaScript 30: object where any method call obj.method() returns the method name string.

        Algorithm:
        - __getattr__ returns a callable that returns the attribute name.

        Complexity: O(1) per call.
        """
        return _Infinite()


def createInfiniteObject() -> Any:
    """
    Interview explanation:
    Top-level LeetCode-style createInfiniteObject API.

    Algorithm:
    - Delegate to Solution.createInfiniteObject.

    Complexity: O(1).
    """
    return Solution().createInfiniteObject()
# @lc code=end
