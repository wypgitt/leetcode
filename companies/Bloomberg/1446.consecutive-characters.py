#
# @lc app=leetcode id=1446 lang=python3
#
# [1446] Consecutive Characters
#
# https://leetcode.com/problems/consecutive-characters/description/
#
# algorithms
# Easy (60.39%)
# Likes:    1862
# Dislikes: 35
# Total Accepted:    240K
# Total Submissions: 397K
# Testcase Example:  "\"leetcode\""
#
# The power of the string is the maximum length of a non-empty substring that
# contains only one unique character.
#
# Given a string s, return the power of s.
#
# Example 1:
#
# Input: s = "leetcode"
# Output: 2
# Explanation: The substring "ee" is of length 2 with the character 'e' only.
#
# Example 2:
#
# Input: s = "abbcccddddeeeeedcba"
# Output: 5
# Explanation: The substring "eeeee" is of length 5 with the character 'e'
# only.
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def maxPower(self, s: str) -> int:
        """
        Interview explanation:
        Power = longest run of identical characters. One pass track current streak.

        Algorithm:
        - cur=ans=1; for i in 1..n-1: if s[i]==s[i-1]: cur++ else cur=1; ans=max

        Complexity: O(n) time, O(1) space.
        """
        ans = cur = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                cur += 1
                ans = max(ans, cur)
            else:
                cur = 1
        return ans

    def maxPower_groupby(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: itertools.groupby over runs; take max length.

        Algorithm:
        - max(len(list(g)) for _, g in groupby(s))

        Complexity: O(n) time, O(n) space for groups.
        """
        from itertools import groupby
        return max(len(list(g)) for _, g in groupby(s))
# @lc code=end
