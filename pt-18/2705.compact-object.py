#
# @lc app=leetcode id=2705 lang=python3
#
# [2705] Compact Object
#
# https://leetcode.com/problems/compact-object/description/
#
# algorithms
# Medium (68.22%)
# Likes:    231
# Dislikes: 25
# Total Accepted:    50.1K
# Total Submissions: 73.4K
# Testcase Example:  "[null, 0, false, 1]"
#
# Given an object or array obj, return a compact object.
#
# A compact object is the same as the original object, except with keys
# containing falsy values removed. This operation applies to the object and any
# nested objects. Arrays are considered objects where the indices are keys. A
# value is considered falsy when Boolean(value) returns false.
#
# You may assume the obj is the output of JSON.parse. In other words, it is
# valid JSON.
#
#
#
# Example 1:
#
# Input: obj = [null, 0, false, 1]
# Output: [1]
# Explanation: All falsy values have been removed from the array.
#
# Example 2:
#
# Input: obj = {"a": null, "b": [false, 1]}
# Output: {"b": [1]}
# Explanation: obj["a"] and obj["b"][0] had falsy values and were removed.
#
# Example 3:
#
# Input: obj = [null, 0, 5, [0], [false, 16]]
# Output: [5, [], [16]]
# Explanation: obj[0], obj[1], obj[3][0], and obj[4][0] were falsy and removed.
#
#
#
# Constraints:
#
#
# obj is a valid JSON object
#
#
# 2 <= JSON.stringify(obj).length <= 10^6
#

# @lc code=start
from typing import Any


class Solution:
    def compactObject(self, obj: Any) -> Any:
        """
        Interview explanation:
        JavaScript problem (Python analog): deep-remove falsy values from nested
        dicts/lists (False, None, 0, "", []).

        Algorithm:
        - Recurse: for lists keep truthy compacted items; for dicts keep keys whose
          compacted values are truthy; scalars returned as-is.

        Complexity: O(n) time over structure size, O(h) recursion space.
        """
        if isinstance(obj, list):
            out = []
            for x in obj:
                c = self.compactObject(x)
                if c:
                    out.append(c)
            return out
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                c = self.compactObject(v)
                if c:
                    out[k] = c
            return out
        return obj
# @lc code=end
