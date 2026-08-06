#
# @lc app=leetcode id=2633 lang=python3
#
# [2633] Convert Object to JSON String
#
# https://leetcode.com/problems/convert-object-to-json-string/description/
#
# algorithms
# Medium (77.93%)
# Likes:    209
# Dislikes: 12
# Total Accepted:    14.2K
# Total Submissions: 18.2K
# Testcase Example:  "{\"y\":1,\"x\":2}"
#
#
# Given a value, return a valid JSON string of that value. The value can
# be a string, number, array, object, boolean, or null. The returned
# string should not include extra spaces. The order of keys should be the
# same as the order returned by Object.keys().
#
# Please solve it without using the built-in JSON.stringify method.
#
# Example 1:
#
# Input: object = {"y":1,"x":2}
# Output: {"y":1,"x":2}
# Explanation:
# Return the JSON representation.
# Note that the order of keys should be the same as the order returned by
# Object.keys().
#
# Example 2:
#
# Input: object = {"a":"str","b":-12,"c":true,"d":null}
# Output: {"a":"str","b":-12,"c":true,"d":null}
# Explanation:
# The primitives of JSON are strings, numbers, booleans, and null.
#
# Example 3:
#
# Input: object = {"key":{"a":1,"b":[{},null,"Hello"]}}
# Output: {"key":{"a":1,"b":[{},null,"Hello"]}}
# Explanation:
# Objects and arrays can include other objects and arrays.
#
# Example 4:
#
# Input: object = true
# Output: true
# Explanation:
# Primitive types are valid inputs.
#
# Constraints:
#
# value is a valid JSON value
#
# 1 <= JSON.stringify(object).length <= 10^5
#
# maxNestingLevel <= 1000
#
# all strings contain only alphanumeric characters
#
# @lc code=start
from typing import Any


def jsonStringify(object: Any) -> str:
    """
    Interview explanation:
    Manually serialize JSON-like Python values (dict/list/str/num/bool/None)
    without using json.dumps (port of convert object to JSON string).

    Algorithm:
    - Recurse by type: None->null, bool->true/false, numbers as str,
      strings with escaped quotes/backslashes, lists/dicts with commas.

    Complexity: O(n) time and space for output size n.
    """
    if object is None:
        return "null"
    if isinstance(object, bool):
        return "true" if object else "false"
    if isinstance(object, (int, float)):
        # Match JSON number formatting for ints/floats.
        if isinstance(object, float) and object.is_integer():
            return str(int(object))
        return str(object)
    if isinstance(object, str):
        escaped = (
            object.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'
    if isinstance(object, list):
        return "[" + ",".join(jsonStringify(x) for x in object) + "]"
    if isinstance(object, dict):
        parts = []
        for k, v in object.items():
            parts.append(jsonStringify(str(k)) + ":" + jsonStringify(v))
        return "{" + ",".join(parts) + "}"
    raise TypeError(f"Unsupported type: {type(object)!r}")


class Solution:
    def jsonStringify(self, object: Any) -> str:
        """
        Interview explanation:
        Thin Solution wrapper for jsonStringify.

        Algorithm:
        - Delegate to jsonStringify(object).

        Complexity: O(n) time and space.
        """
        return jsonStringify(object)
# @lc code=end
