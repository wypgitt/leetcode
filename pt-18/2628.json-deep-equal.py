#
# @lc app=leetcode id=2628 lang=python3
#
# [2628] JSON Deep Equal
#
# https://leetcode.com/problems/json-deep-equal/description/
#
# algorithms
# Medium (39.73%)
# Likes:    222
# Dislikes: 18
# Total Accepted:    15.3K
# Total Submissions: 38.5K
# Testcase Example:  "{\"x\":1,\"y\":2}\n{\"x\":1,\"y\":2}"
#
#
# Given two values o1 and o2, return a boolean value indicating whether
# two values, o1 and o2, are deeply equal.
#
# For two values to be deeply equal, the following conditions must be met:
#
# If both values are primitive types, they are deeply equal if they pass
# the === equality check.
#
# If both values are arrays, they are deeply equal if they have the same
# elements in the same order, and each element is also deeply equal
# according to these conditions.
#
# If both values are objects, they are deeply equal if they have the same
# keys, and the associated values for each key are also deeply equal
# according to these conditions.
#
# You may assume both values are the output of JSON.parse. In other words,
# they are valid JSON.
#
# Please solve it without using lodash's _.isEqual() function
#
# Example 1:
#
# Input: o1 = {"x":1,"y":2}, o2 = {"x":1,"y":2}
# Output: true
# Explanation: The keys and values match exactly.
#
# Example 2:
#
# Input: o1 = {"y":2,"x":1}, o2 = {"x":1,"y":2}
# Output: true
# Explanation: Although the keys are in a different order, they still
# match exactly.
#
# Example 3:
#
# Input: o1 = {"x":null,"L":[1,2,3]}, o2 = {"x":null,"L":["1","2","3"]}
# Output: false
# Explanation: The array of numbers is different from the array of
# strings.
#
# Example 4:
#
# Input: o1 = true, o2 = false
# Output: false
# Explanation: true !== false
#
# Constraints:
#
# 1 <= JSON.stringify(o1).length <= 10^5
#
# 1 <= JSON.stringify(o2).length <= 10^5
#
# maxNestingDepth <= 1000
#
# @lc code=start
from typing import Any


def areDeeplyEqual(o1: Any, o2: Any) -> bool:
    """
    Interview explanation:
    Deep equality for JSON-like values: None, bool, int/float, str, list, dict.
    Arrays and objects of different types are never equal.

    Algorithm:
    - Same identity or equal primitives => True.
    - Lists: same length and pairwise deep-equal.
    - Dicts: same key set and deep-equal values (key order irrelevant).
    - Otherwise False (including list vs dict).

    Complexity: O(n) time over total nodes, O(d) recursion stack.
    """
    if o1 is o2:
        return True
    # bool is a subclass of int; never treat True/False as 1/0.
    if type(o1) is not type(o2):
        if isinstance(o1, bool) or isinstance(o2, bool):
            return False
        if isinstance(o1, (int, float)) and isinstance(o2, (int, float)):
            return o1 == o2
        return False
    if isinstance(o1, list):
        if len(o1) != len(o2):
            return False
        return all(areDeeplyEqual(a, b) for a, b in zip(o1, o2))
    if isinstance(o1, dict):
        if o1.keys() != o2.keys():
            return False
        return all(areDeeplyEqual(o1[k], o2[k]) for k in o1)
    return o1 == o2


class Solution:
    def areDeeplyEqual(self, o1: Any, o2: Any) -> bool:
        """
        Interview explanation:
        Thin Solution wrapper for JSON deep equal.

        Algorithm:
        - Delegate to areDeeplyEqual(o1, o2).

        Complexity: Same as areDeeplyEqual.
        """
        return areDeeplyEqual(o1, o2)
# @lc code=end
