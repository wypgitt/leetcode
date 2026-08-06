#
# @lc app=leetcode id=14 lang=python3
#
# [14] Longest Common Prefix
#
# https://leetcode.com/problems/longest-common-prefix/description/
#
# algorithms
# Easy (48.11%)
# Likes:    21676
# Dislikes: 4953
# Total Accepted:    6.1M
# Total Submissions: 13M
# Testcase Example:  "[\"flower\",\"flow\",\"flight\"]"
#
# Write a function to find the longest common prefix string amongst an array of
# strings.
#
# If there is no common prefix, return an empty string "".
#
# Example 1:
#
# Input: strs = ["flower","flow","flight"]
# Output: "fl"
#
# Example 2:
#
# Input: strs = ["dog","racecar","car"]
# Output: ""
# Explanation: There is no common prefix among the input strings.
#
# Constraints:
#
# 1 <= strs.length <= 200
#
# 0 <= strs[i].length <= 200
#
# strs[i] consists of only lowercase English letters if it is non-empty.
#

# @lc code=start
from typing import List


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        """
        Interview explanation:
        Find the longest string that is a prefix of every string in the list.
        Vertical scan compares one character column at a time and can exit
        early when prefixes diverge.

        Algorithm:
        - Use the first string as a candidate character-by-character.
        - For each column index i, compare strs[0][i] against every other string.
        - Return the prefix as soon as a mismatch or end-of-string is found.

        Complexity: O(S) time where S is total characters across all strings,
        O(1) extra space.
        """
        if not strs:
            return ""

        for i, ch in enumerate(strs[0]):
            for s in strs[1:]:
                if i == len(s) or s[i] != ch:
                    return strs[0][:i]
        return strs[0]

    def longestCommonPrefixHorizontal(self, strs: List[str]) -> str:
        """
        Interview explanation:
        Horizontal scan starts with the first string as the candidate prefix
        and shrinks it until it is a prefix of every remaining string.

        Algorithm:
        - Start with prefix = strs[0].
        - For each next string, shrink prefix while it is not a prefix of that
          string.
        - Empty prefix means no common prefix; return "".

        Complexity: O(S) time where S is total characters across all strings,
        O(1) extra space.
        """
        if not strs:
            return ""

        prefix = strs[0]
        for s in strs[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix
# @lc code=end
