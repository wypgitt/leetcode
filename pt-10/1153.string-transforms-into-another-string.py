#
# @lc app=leetcode id=1153 lang=python3
#
# [1153] String Transforms Into Another String
#
# https://leetcode.com/problems/string-transforms-into-another-string/description/
#
# algorithms
# Hard (34.62%)
# Likes:    889
# Dislikes: 339
# Total Accepted:    54.7K
# Total Submissions: 157.9K
# Testcase Example:  "\"aabcc\"\n\"ccdee\""
#
#
# Given two strings str1 and str2 of the same length, determine whether
# you can transform str1 into str2 by doing zero or more conversions.
#
# In one conversion you can convert all occurrences of one character in
# str1 to any other lowercase English character.
#
# Return true if and only if you can transform str1 into str2.
#
# Example 1:
#
# Input: str1 = "aabcc", str2 = "ccdee"
# Output: true
# Explanation: Convert 'c' to 'e' then 'b' to 'd' then 'a' to 'c'. Note
# that the order of conversions matter.
#
# Example 2:
#
# Input: str1 = "leetcode", str2 = "codeleet"
# Output: false
# Explanation: There is no way to transform str1 to str2.
#
# Constraints:
#
# 1 <= str1.length == str2.length <= 10^4
#
# str1 and str2 contain only lowercase English letters.
#
# @lc code=start
from typing import Dict


class Solution:
    def canConvert(self, str1: str, str2: str) -> bool:
        """
        Interview explanation:
        Premium. Convert str1→str2 by transforming characters (all occurrences
        of a letter at once). Mapping must be a function; cycles need a free
        temporary character unless str1 already equals str2.

        Algorithm:
        - If str1==str2: True.
        - Build mapping char1→char2; conflict if same source maps to two targets.
        - If len(set(str2))==26, no temp char for breaking cycles → False.
        - Otherwise True (mappings/chains/cycles can be resolved with a spare).

        Complexity: O(n) time, O(1) alphabet space.
        """
        if str1 == str2:
            return True
        mp: Dict[str, str] = {}
        for a, b in zip(str1, str2):
            if a in mp and mp[a] != b:
                return False
            mp[a] = b
        return len(set(str2)) < 26
# @lc code=end
