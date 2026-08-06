#
# @lc app=leetcode id=2775 lang=python3
#
# [2775] Undefined to Null
#
# https://leetcode.com/problems/undefined-to-null/description/
#
# algorithms
# Medium (70.19%)
# Likes:    15
# Dislikes: 1
# Total Accepted:    1.1K
# Total Submissions: 1.5K
# Testcase Example:  "{\"a\": undefined, \"b\":3}"
#
#
# Given a deeply nested object or array obj, return the object obj with
# any undefined values replaced by null.
#
# undefined values are handled differently than null values when objects
# are converted to a JSON string using JSON.stringify(). This function
# helps ensure serialized data is free of unexpected errors.
#
# Example 1:
#
# Input: obj = {"a": undefined, "b": 3}
# Output: {"a": null, "b": 3}
# Explanation: The value for obj.a has been changed from undefined to null
#
# Example 2:
#
# Input: obj = {"a": undefined, "b": ["a", undefined]}
# Output: {"a": null,"b": ["a", null]}
# Explanation: The values for obj.a and obj.b[1] have been changed from
# undefined to null
#
# Constraints:
#
# obj is a valid JSON object or array
#
# 2 <= JSON.stringify(obj).length <= 10^5
#
# @lc code=start
from typing import Any

# Sentinel used in this Python port to stand in for JS `undefined`.
UNDEFINED = object()


class Solution:
    def undefinedToNull(self, obj: Any) -> Any:
        """
        Interview explanation:
        JS premium: recursively replace undefined with null in objects/arrays.
        Python port: convert UNDEFINED sentinel and Ellipsis to None; recurse
        into dicts/lists. Existing None stays null.

        Algorithm:
        - If value is UNDEFINED or Ellipsis -> None.
        - Recurse lists/dicts; return other primitives as-is.

        Complexity: O(N) nodes.
        """
        if obj is UNDEFINED or obj is ...:
            return None
        if isinstance(obj, list):
            return [self.undefinedToNull(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self.undefinedToNull(v) for k, v in obj.items()}
        return obj
# @lc code=end
