#
# @lc app=leetcode id=2635 lang=python3
#
# [2635] Apply Transform Over Each Element in Array
#
# https://leetcode.com/problems/apply-transform-over-each-element-in-array/description/
#
# algorithms
# Easy (86.19%)
# Likes:    929
# Dislikes: 120
# Total Accepted:    352.8K
# Total Submissions: 409.4K
# Testcase Example:  "function plusone(n) { return n + 1; }\n[1,2,3]"
#
# Given an integer array arr and a mapping function fn, return a new array with
# a transformation applied to each element.
#
# The returned array should be created such that returnedArray[i] = fn(arr[i],
# i).
#
# Please solve it without the built-in Array.map method.
#
#
#
# Example 1:
#
# Input: arr = [1,2,3], fn = function plusone(n) { return n + 1; }
# Output: [2,3,4]
# Explanation:
# const newArray = map(arr, plusone); // [2,3,4]
# The function increases each value in the array by one.
#
# Example 2:
#
# Input: arr = [1,2,3], fn = function plusI(n, i) { return n + i; }
# Output: [1,3,5]
# Explanation: The function increases each value by the index it resides in.
#
# Example 3:
#
# Input: arr = [10,20,30], fn = function constant() { return 42; }
# Output: [42,42,42]
# Explanation: The function always returns 42.
#
#
#
# Constraints:
#
#
# 0 <= arr.length <= 1000
#
#
# -10^9 <= arr[i] <= 10^9
#
#
# fn returns an integer.
#

# @lc code=start
from typing import Any, Callable, List


def map(arr: List[Any], fn: Callable[..., Any]) -> List[Any]:
    """
    Interview explanation:
    Map each element with fn(value, index) without using built-in map.

    Algorithm:
    - Build returnedArray[i] = fn(arr[i], i) for all indices.

    Complexity: O(n) time and space.
    """
    return [fn(arr[i], i) for i in range(len(arr))]


class Solution:
    def map(self, arr: List[Any], fn: Callable[..., Any]) -> List[Any]:
        """
        Interview explanation:
        Thin Solution wrapper for map.

        Algorithm:
        - Delegate to map(arr, fn).

        Complexity: O(n) time and space.
        """
        return map(arr, fn)
# @lc code=end
