#
# @lc app=leetcode id=2727 lang=python3
#
# [2727] Is Object Empty
#
# https://leetcode.com/problems/is-object-empty/description/
#
# algorithms
# Easy (82.01%)
# Likes:    226
# Dislikes: 16
# Total Accepted:    125.4K
# Total Submissions: 152.9K
# Testcase Example:  "{\"x\": 5, \"y\": 42}"
#
# Given an object or an array, return if it is empty.
#
#
# An empty object contains no key-value pairs.
#
#
# An empty array contains no elements.
#
# You may assume the object or array is the output of JSON.parse.
#
#
#
# Example 1:
#
# Input: obj = {"x": 5, "y": 42}
# Output: false
# Explanation: The object has 2 key-value pairs so it is not empty.
#
# Example 2:
#
# Input: obj = {}
# Output: true
# Explanation: The object doesn't have any key-value pairs so it is empty.
#
# Example 3:
#
# Input: obj = [null, false, 0]
# Output: false
# Explanation: The array has 3 elements so it is not empty.
#
#
#
# Constraints:
#
#
# obj is a valid JSON object or array
#
#
# 2 <= JSON.stringify(obj).length <= 10^5
#
#
#
# Can you solve it in O(1) time?
#

# @lc code=start
from typing import Any


class Solution:
    def isEmpty(self, obj: Any) -> bool:
        """
        Interview explanation:
        JavaScript problem (Python analog): true if object/array has no keys/elements.

        Algorithm:
        - For dict/list/tuple return len==0; else False.

        Complexity: O(1).
        """
        if isinstance(obj, (dict, list, tuple, set, str)):
            return len(obj) == 0
        return False
# @lc code=end
