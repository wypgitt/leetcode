#
# @lc app=leetcode id=2619 lang=python3
#
# [2619] Array Prototype Last
#
# https://leetcode.com/problems/array-prototype-last/description/
#
# algorithms
# Easy (74.68%)
# Likes:    626
# Dislikes: 28
# Total Accepted:    254.5K
# Total Submissions: 340.8K
# Testcase Example:  "[null, {}, 3]"
#
# Write code that enhances all arrays such that you can call
# the array.last() method on any array and it will return the last element. If
# there are no elements in the array, it should return -1.
#
# You may assume the array is the output of JSON.parse.
#
#
#
# Example 1:
#
# Input: nums = [null, {}, 3]
# Output: 3
# Explanation: Calling nums.last() should return the last element: 3.
#
# Example 2:
#
# Input: nums = []
# Output: -1
# Explanation: Because there are no elements, return -1.
#
#
#
# Constraints:
#
#
# arr is a valid JSON array
#
#
# 0 <= arr.length <= 1000
#

# @lc code=start
from typing import Any, List


def last(arr: List[Any]) -> Any:
    """
    Interview explanation:
    Port of Array.prototype.last: return the last element, or -1 if empty.

    Algorithm:
    - If arr is non-empty return arr[-1], else return -1.

    Complexity: O(1) time and space.
    """
    return arr[-1] if arr else -1


class Solution:
    def last(self, arr: List[Any]) -> Any:
        """
        Interview explanation:
        Thin Solution wrapper for array last.

        Algorithm:
        - Delegate to last(arr).

        Complexity: O(1) time and space.
        """
        return last(arr)
# @lc code=end
