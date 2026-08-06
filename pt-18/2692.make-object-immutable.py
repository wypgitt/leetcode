#
# @lc app=leetcode id=2692 lang=python3
#
# [2692] Make Object Immutable
#
# https://leetcode.com/problems/make-object-immutable/description/
#
# algorithms
# Medium (62.82%)
# Likes:    17
# Dislikes: 1
# Total Accepted:    767
# Total Submissions: 1.2K
# Testcase Example:  "{\"x\":5}\n(obj) => { obj.x = 5; return obj.x; }"
#
#
# Write a function that takes an object obj and returns a new immutable
# version of this object.
#
# An immutable object is an object that can't be altered and will throw an
# error if any attempt is made to alter it.
#
# There are three types of error messages that can be produced from this
# new object.
#
# Attempting to modify a key on the object will result in this error
# message: `Error Modifying: ${key}`.
#
# Attempting to modify an index on an array will result in this error
# message: `Error Modifying Index: ${index}`.
#
# Attempting to call a method that mutates an array will result in this
# error message: `Error Calling Method: ${methodName}`. You may assume the
# only methods that can mutate an array are ['pop', 'push', 'shift',
# 'unshift', 'splice', 'sort', 'reverse'].
#
# obj is a valid JSON object or array, meaning it is the output of
# JSON.parse().
#
# Note that a string literal should be thrown, not an Error.
#
# Example 1:
#
# Input:
# obj = {
#   "x": 5
# }
# fn = (obj) => {
#   obj.x = 5;
#   return obj.x;
# }
# Output: {"value": null, "error": "Error Modifying: x"}
# Explanation: Attempting to modify a key on an object resuts in a thrown
# error. Note that it doesn't matter that the value was set to the same
# value as it was before.
#
# Example 2:
#
# Input:
# obj = [1, 2, 3]
# fn = (arr) => {
#   arr[1] = {};
#   return arr[2];
# }
# Output: {"value": null, "error": "Error Modifying Index: 1"}
# Explanation: Attempting to modify an array results in a thrown error.
#
# Example 3:
#
# Input:
# obj = {
#   "arr": [1, 2, 3]
# }
# fn = (obj) => {
#   obj.arr.push(4);
#   return 42;
# }
# Output: { "value": null, "error": "Error Calling Method: push"}
# Explanation: Calling a method that can result in a mutation results in a
# thrown error.
#
# Example 4:
#
# Input:
# obj = {
#   "x": 2,
#   "y": 2
# }
# fn = (obj) => {
#   return Object.keys(obj);
# }
# Output: {"value": ["x", "y"], "error": null}
# Explanation: No mutations were attempted so the function returns as
# normal.
#
# Constraints:
#
# obj is a valid JSON object or array
#
# 2 <= JSON.stringify(obj).length <= 10^5
#
# @lc code=start

from typing import Any


class _ImmutableProxy:
    def __init__(self, obj: Any):
        """
        Interview explanation:
        Internal proxy holding a dict/list; blocks mutation and wraps nested access.

        Algorithm:
        - Store obj via object.__setattr__ to bypass our __setattr__.

        Complexity: O(1).
        """
        object.__setattr__(self, "_obj", obj)

    def __getattr__(self, name: str) -> Any:
        val = getattr(object.__getattribute__(self, "_obj"), name)
        return makeImmutable(val) if isinstance(val, (dict, list)) else val

    def __getitem__(self, key: Any) -> Any:
        val = object.__getattribute__(self, "_obj")[key]
        return makeImmutable(val) if isinstance(val, (dict, list)) else val

    def __setattr__(self, name: str, value: Any) -> None:
        raise RuntimeError("Immutable object cannot be modified")

    def __setitem__(self, key: Any, value: Any) -> None:
        raise RuntimeError("Immutable object cannot be modified")

    def __delattr__(self, name: str) -> None:
        raise RuntimeError("Immutable object cannot be modified")

    def __delitem__(self, key: Any) -> None:
        raise RuntimeError("Immutable object cannot be modified")


def makeImmutable(obj: Any) -> Any:
    """
    Interview explanation:
    JavaScript 30: return a deeply immutable proxy of obj; mutations throw.

    Algorithm:
    - Wrap dict/list in proxy that rejects set/del and wraps nested values on access.

    Complexity: O(1) wrap; O(1) per access.
    """
    if isinstance(obj, (dict, list)):
        return _ImmutableProxy(obj)
    return obj


class Solution:
    def makeImmutable(self, obj: Any) -> Any:
        """
        Interview explanation:
        Solution method wrapping makeImmutable for consistency with other ports.

        Algorithm:
        - Delegate to module-level makeImmutable.

        Complexity: O(1).
        """
        return makeImmutable(obj)
# @lc code=end
