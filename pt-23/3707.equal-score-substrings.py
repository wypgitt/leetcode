#
# @lc app=leetcode id=3707 lang=python3
#
# [3707] Equal Score Substrings
#
# https://leetcode.com/problems/equal-score-substrings/description/
#
# algorithms
# Easy (57.00%)
# Likes:    42
# Dislikes: 3
# Total Accepted:    39.3K
# Total Submissions: 68.9K
# Testcase Example:  "\"adcb\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# The score of a string is the sum of the positions of its characters in
# the alphabet, where 'a' = 1, 'b' = 2, ..., 'z' = 26.
#
# Determine whether there exists an index i such that the string can be
# split into two non-empty substrings s[0..i] and s[(i + 1)..(n - 1)] that
# have equal scores.
#
# Return true if such a split exists, otherwise return false.
#
# Example 1:
#
# Input: s = "adcb"
#
# Output: true
#
# Explanation:
#
# Split at index i = 1:
#
# Left substring = s[0..1] = "ad" with score = 1 + 4 = 5
#
# Right substring = s[2..3] = "cb" with score = 3 + 2 = 5
#
# Both substrings have equal scores, so the output is true.
#
# Example 2:
#
# Input: s = "bace"
#
# Output: false
#
# Explanation:​​​​​​
#
# ​​​​​​​No split produces equal scores, so the output is false.
#
# Constraints:
#
# 2 <= s.length <= 100
#
# s consists of lowercase English letters.
#

# @lc code=start

class Solution:
    def scoreBalance(self, s: str) -> bool:
        """
        Interview explanation:
        Split scores are equal iff total score is even and some proper prefix
        equals half the total.

        Algorithm:
        - total = sum(ord(c) - 96); if odd, false.
        - Scan prefixes (leave at least one char on the right); check == total/2.

        Complexity: O(n) time, O(1) space.
        """
        total = sum(ord(c) - 96 for c in s)
        if total & 1:
            return False
        half, cur = total // 2, 0
        for i in range(len(s) - 1):
            cur += ord(s[i]) - 96
            if cur == half:
                return True
        return False

    def scoreBalance_suffix(self, s: str) -> bool:
        """
        Interview explanation:
        Alternate: grow a suffix sum and test against half.

        Algorithm:
        - Same parity check; accumulate from the right instead.

        Complexity: O(n) time, O(1) space.
        """
        total = sum(ord(c) - 96 for c in s)
        if total & 1:
            return False
        half, cur = total // 2, 0
        for i in range(len(s) - 1, 0, -1):
            cur += ord(s[i]) - 96
            if cur == half:
                return True
        return False
# @lc code=end
