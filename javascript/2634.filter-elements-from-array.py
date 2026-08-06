#
# @lc app=leetcode id=2634 lang=python3
#
# [2634] Filter Elements from Array
#
# https://leetcode.com/problems/filter-elements-from-array/description/
#
# algorithms
# Easy (85.55%)
# Likes:    825
# Dislikes: 111
# Total Accepted:    322.7K
# Total Submissions: 377.2K
# Testcase Example:  "function greaterThan10(n) { return n > 10; }\n[0,10,20,30]"
#
# Given an integer array arr and a filtering function fn, return a filtered
# array filteredArr.
#
# The fn function takes one or two arguments:
#
#
# arr[i] - number from the arr
#
#
# i - index of arr[i]
#
# filteredArr should only contain the elements from the arr for which the
# expression fn(arr[i], i) evaluates to a truthy value. A truthy value is a
# value where Boolean(value) returns true.
#
# Please solve it without the built-in Array.filter method.
#
#
#
# Example 1:
#
# Input: arr = [0,10,20,30], fn = function greaterThan10(n) { return n > 10; }
# Output: [20,30]
# Explanation:
# const newArray = filter(arr, fn); // [20, 30]
# The function filters out values that are not greater than 10
#
# Example 2:
#
# Input: arr = [1,2,3], fn = function firstIndex(n, i) { return i === 0; }
# Output: [1]
# Explanation:
# fn can also accept the index of each element
# In this case, the function removes elements not at index 0
#
# Example 3:
#
# Input: arr = [-2,-1,0,1,2], fn = function plusOne(n) { return n + 1 }
# Output: [-2,0,1,2]
# Explanation:
# Falsey values such as 0 should be filtered out
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

# @lc code=start
from typing import Any, Callable, List


def filter(arr: List[Any], fn: Callable[..., Any]) -> List[Any]:
    """
    Interview explanation:
    Filter arr keeping elements where fn(value, index) is truthy, without
    using built-in filter.

    Algorithm:
    - Enumerate arr; append item when bool(fn(item, i)) is True.

    Complexity: O(n) time, O(n) space for the result.
    """
    out: List[Any] = []
    for i, x in enumerate(arr):
        if fn(x, i):
            out.append(x)
    return out


class Solution:
    def filter(self, arr: List[Any], fn: Callable[..., Any]) -> List[Any]:
        """
        Interview explanation:
        Thin Solution wrapper for filter.

        Algorithm:
        - Delegate to filter(arr, fn).

        Complexity: O(n) time and space.
        """
        return filter(arr, fn)
# @lc code=end
