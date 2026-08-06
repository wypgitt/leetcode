#
# @lc app=leetcode id=2700 lang=python3
#
# [2700] Differences Between Two Objects
#
# https://leetcode.com/problems/differences-between-two-objects/description/
#
# algorithms
# Medium (74.47%)
# Likes:    146
# Dislikes: 31
# Total Accepted:    7.9K
# Total Submissions: 10.6K
# Testcase Example:  "{}\n{\"a\": 1, \"b\": 2}"
#
#
# Write a function that accepts two deeply nested objects or arrays obj1
# and obj2 and returns a new object representing their differences.
#
# The function should compare the properties of the two objects and
# identify any changes. The returned object should only contains keys
# where the value is different from obj1 to obj2.
#
# For each changed key, the value should be represented as an array [obj1
# value, obj2 value]. Keys that exist in one object but not in the other
# should not be included in the returned object. The end result should be
# a deeply nested object where each leaf value is a difference array.
#
# When comparing two arrays, the indices of the arrays are considered to
# be their keys.
#
# You may assume that both objects are the output of JSON.parse.
#
# Example 1:
#
# Input:
# obj1 = {}
# obj2 = {
#   "a": 1,
#   "b": 2
# }
# Output: {}
# Explanation: There were no modifications made to obj1. New keys "a" and
# "b" appear in obj2, but keys that are added or removed should be
# ignored.
#
# Example 2:
#
# Input:
# obj1 = {
#   "a": 1,
#   "v": 3,
#   "x": [],
#   "z": {
#     "a": null
#   }
# }
# obj2 = {
#   "a": 2,
#   "v": 4,
#   "x": [],
#   "z": {
#     "a": 2
#   }
# }
# Output:
# {
#   "a": [1, 2],
#   "v": [3, 4],
#   "z": {
#     "a": [null, 2]
#   }
# }
# Explanation: The keys "a", "v", and "z" all had changes applied. "a" was
# changed from 1 to 2. "v" was changed from 3 to 4. "z" had a change
# applied to a child object. "z.a" was changed from null to 2.
#
# Example 3:
#
# Input:
# obj1 = {
#   "a": 5,
#   "v": 6,
#   "z": [1, 2, 4, [2, 5, 7]]
# }
# obj2 = {
#   "a": 5,
#   "v": 7,
#   "z": [1, 2, 3, [1]]
# }
# Output:
# {
#   "v": [6, 7],
#   "z": {
#     "2": [4, 3],
#     "3": {
#       "0": [2, 1]
#     }
#   }
# }
# Explanation: In obj1 and obj2, the keys "v" and "z" have different
# assigned values. "a" is ignored because the value is unchanged. In the
# key "z", there is a nested array. Arrays are treated like objects where
# the indices are keys. There were two alterations to the the array: z[2]
# and z[3][0]. z[0] and z[1] were unchanged and thus not included. z[3][1]
# and z[3][2] were removed and thus not included.
#
# Example 4:
#
# Input:
# obj1 = {
#   "a": {"b": 1},
# }
# obj2 = {
#   "a": [5],
# }
# Output:
# {
#   "a": [{"b": 1}, [5]]
# }
# Explanation: The key "a" exists in both objects. Since the two
# associated values have different types, they are placed in the
# difference array.
#
# Example 5:
#
# Input:
# obj1 = {
#   "a": [1, 2, {}],
#   "b": false
# }
# obj2 = {
#   "b": false,
#   "a": [1, 2, {}]
# }
# Output:
# {}
# Explanation: Apart from a different ordering of keys, the two objects
# are identical so an empty object is returned.
#
# Constraints:
#
# obj1 and obj2 are valid JSON objects or arrays
#
# 2 <= JSON.stringify(obj1).length <= 10^4
#
# 2 <= JSON.stringify(obj2).length <= 10^4
#
# @lc code=start

from typing import Any, Dict


def objDiff(obj1: Any, obj2: Any) -> Any:
    """
    Interview explanation:
    JavaScript 30: deep difference of two JSON-like objects/arrays. For equal primitives return
    nothing; for differing leaves return [v1, v2]; for objects/arrays return nested diffs of keys
    present in both with differences. Keys only in one side are ignored.

    Algorithm:
    - Recurse: if types differ or one is nullish mismatch -> [obj1,obj2]; if both dict/list recurse
      on shared keys/indices; omit empty nested diffs.

    Complexity: O(size) time and space.
    """
    if type(obj1) != type(obj2):
        return [obj1, obj2]
    if isinstance(obj1, dict):
        diff: Dict[str, Any] = {}
        for k in obj1:
            if k in obj2:
                d = objDiff(obj1[k], obj2[k])
                if d != {}:
                    diff[k] = d
        return diff
    if isinstance(obj1, list):
        diff_l: Dict[str, Any] = {}
        for i in range(min(len(obj1), len(obj2))):
            d = objDiff(obj1[i], obj2[i])
            if d != {}:
                diff_l[str(i)] = d
        return diff_l
    if obj1 == obj2:
        return {}
    return [obj1, obj2]


class Solution:
    def objDiff(self, obj1: Any, obj2: Any) -> Any:
        """
        Interview explanation:
        Solution method for object deep diff Python port.

        Algorithm:
        - Delegate to module-level objDiff.

        Complexity: O(size).
        """
        return objDiff(obj1, obj2)
# @lc code=end
