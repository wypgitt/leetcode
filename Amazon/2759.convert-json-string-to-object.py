#
# @lc app=leetcode id=2759 lang=python3
#
# [2759] Convert JSON String to Object
#
# https://leetcode.com/problems/convert-json-string-to-object/description/
#
# algorithms
# Hard (61.88%)
# Likes:    17
# Dislikes: 4
# Total Accepted:    982
# Total Submissions: 1.6K
# Testcase Example:  "'{\"a\":2,\"b\":[1,2,3]}'"
#
#
# Given a string str, return parsed JSON parsedStr. You may assume the str
# is a valid JSON string hence it only includes strings, numbers, arrays,
# objects, booleans, and null. str will not include invisible characters
# and escape characters.
#
# Please solve it without using the built-in JSON.parse method.
#
# Example 1:
#
# Input: str = '{"a":2,"b":[1,2,3]}'
# Output: {"a":2,"b":[1,2,3]}
# Explanation: Returns the object represented by the JSON string.
#
# Example 2:
#
# Input: str = 'true'
# Output: true
# Explanation: Primitive types are valid JSON.
#
# Example 3:
#
# Input: str = '[1,5,"false",{"a":2}]'
# Output: [1,5,"false",{"a":2}]
# Explanation: Returns the array represented by the JSON string.
#
# Constraints:
#
# str is a valid JSON string
#
# 1 <= str.length <= 10^5
#
# @lc code=start
from typing import Any


class Solution:
    def jsonParse(self, s: str) -> Any:
        """
        Interview explanation:
        JS premium hard: implement JSON.parse via recursive descent (no json module).

        Algorithm:
        - parse_value dispatches on '{', '[', '"', t/f/n, or number.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        i = 0

        def parse_value() -> Any:
            nonlocal i
            c = s[i]
            if c == "{":
                return parse_object()
            if c == "[":
                return parse_array()
            if c == '"':
                return parse_string()
            if c == "t":
                i += 4
                return True
            if c == "f":
                i += 5
                return False
            if c == "n":
                i += 4
                return None
            return parse_number()

        def parse_string() -> str:
            nonlocal i
            i += 1
            out = []
            while i < n:
                c = s[i]
                if c == '"':
                    i += 1
                    break
                if c == "\\":
                    i += 1
                    out.append(s[i])
                else:
                    out.append(c)
                i += 1
            return "".join(out)

        def parse_number() -> Any:
            nonlocal i
            start = i
            while i < n and s[i] not in ",}]":
                i += 1
            text = s[start:i]
            if any(ch in text for ch in ".eE"):
                return float(text)
            return int(text)

        def parse_array() -> list:
            nonlocal i
            arr = []
            i += 1
            while i < n:
                if s[i] == "]":
                    i += 1
                    break
                if s[i] == ",":
                    i += 1
                    continue
                arr.append(parse_value())
            return arr

        def parse_object() -> dict:
            nonlocal i
            obj = {}
            i += 1
            while i < n:
                if s[i] == "}":
                    i += 1
                    break
                if s[i] == ",":
                    i += 1
                    continue
                key = parse_string()
                i += 1  # ':'
                obj[key] = parse_value()
            return obj

        return parse_value()
# @lc code=end
