#
# @lc app=leetcode id=2794 lang=python3
#
# [2794] Create Object from Two Arrays
#
# https://leetcode.com/problems/create-object-from-two-arrays/description/
#
# algorithms
# Easy (64.73%)
# Likes:    11
# Dislikes: 3
# Total Accepted:    1.9K
# Total Submissions: 2.9K
# Testcase Example:  "[\"a\",\"b\",\"c\"]\n[1,2,3]"
#
#
# Given two arrays keysArr and valuesArr, return a new object obj. Each
# key-value pair in obj should come from keysArr[i] and valuesArr[i].
#
# If a duplicate key exists at a previous index, that key-value should be
# excluded. In other words, only the first key should be added to the
# object.
#
# If the key is not a string, it should be converted into a string by
# calling String() on it.
#
# Example 1:
#
# Input: keysArr = ["a", "b", "c"], valuesArr = [1, 2, 3]
# Output: {"a": 1, "b": 2, "c": 3}
# Explanation: The keys "a", "b", and "c" are paired with the values 1, 2,
# and 3 respectively.
#
# Example 2:
#
# Input: keysArr = ["1", 1, false], valuesArr = [4, 5, 6]
# Output: {"1": 4, "false": 6}
# Explanation: First, all the elements in keysArr are converted into
# strings. We can see there are two occurrences of "1". The value
# associated with the first occurrence of "1" is used: 4.
#
# Example 3:
#
# Input: keysArr = [], valuesArr = []
# Output: {}
# Explanation: There are no keys so an empty object is returned.
#
# Constraints:
#
# keysArr and valuesArr are valid JSON arrays
#
# 2 <= JSON.stringify(keysArr).length, JSON.stringify(valuesArr).length <=
# 5 * 10^5
#
# keysArr.length === valuesArr.length
#
# @lc code=start
from typing import Any, Dict, List


class Solution:
    def createObject(self, keysArr: List[Any], valuesArr: List[Any]) -> Dict[str, Any]:
        """
        Interview explanation:
        JS premium: build object from parallel key/value arrays; stringify keys;
        first occurrence wins on duplicate keys.

        Algorithm:
        - Iterate indices; set ans[str(key)] only if key not yet present.

        Complexity: O(n) time, O(n) space.
        """
        ans: Dict[str, Any] = {}
        for i in range(len(keysArr)):
            k = str(keysArr[i])
            if k not in ans:
                ans[k] = valuesArr[i] if i < len(valuesArr) else None
        return ans
# @lc code=end
