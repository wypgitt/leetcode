#
# @lc app=leetcode id=1422 lang=python3
#
# [1422] Maximum Score After Splitting a String
#
# https://leetcode.com/problems/maximum-score-after-splitting-a-string/description/
#
# algorithms
# Easy (65.06%)
# Likes:    2209
# Dislikes: 91
# Total Accepted:    379K
# Total Submissions: 583K
# Testcase Example:  "\"011101\""
#
# Given a string s of zeros and ones, return the maximum score after splitting
# the string into two non-empty substrings (i.e. left substring and right
# substring).
#
# The score after splitting a string is the number of zeros in the left
# substring plus the number of ones in the right substring.
#
# Example 1:
#
# Input: s = "011101"
# Output: 5
# Explanation:
# All possible ways of splitting s into two non-empty substrings are:
# left = "0" and right = "11101", score = 1 + 4 = 5
# left = "01" and right = "1101", score = 1 + 3 = 4
# left = "011" and right = "101", score = 1 + 2 = 3
# left = "0111" and right = "01", score = 1 + 1 = 2
# left = "01110" and right = "1", score = 2 + 1 = 3
#
# Example 2:
#
# Input: s = "00111"
# Output: 5
# Explanation: When left = "00" and right = "111", we get the maximum score = 2
# + 3 = 5
#
# Example 3:
#
# Input: s = "1111"
# Output: 3
#
# Constraints:
#
# 2 <= s.length <= 500
#
# The string s consists of characters '0' and '1' only.
#

# @lc code=start
class Solution:
    def maxScore(self, s: str) -> int:
        """
        Interview explanation:
        Split into non-empty left|right; score = zeros_left + ones_right.
        ones_right = total_ones - ones_left. Scan split points; track zeros/ones left.

        Algorithm:
        (one pass)
        - total_ones = count('1'); best=0; z=o=0; for i in 0..n-2: update; best=max(z+total-o)

        Complexity: O(n) time, O(1) space.
        """
        total_ones = s.count("1")
        best = z = o = 0
        for i in range(len(s) - 1):
            if s[i] == "0":
                z += 1
            else:
                o += 1
            best = max(best, z + total_ones - o)
        return best

    def maxScore_prefix(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: compute prefix zeros and suffix ones arrays; max sum at splits.

        Algorithm:
        - pref_z[i], suf_o[i]; max pref_z[i]+suf_o[i+1] for i in 0..n-2.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        pref_z = [0] * n
        suf_o = [0] * n
        pref_z[0] = 1 if s[0] == "0" else 0
        for i in range(1, n):
            pref_z[i] = pref_z[i - 1] + (s[i] == "0")
        suf_o[-1] = 1 if s[-1] == "1" else 0
        for i in range(n - 2, -1, -1):
            suf_o[i] = suf_o[i + 1] + (s[i] == "1")
        return max(pref_z[i] + suf_o[i + 1] for i in range(n - 1))
# @lc code=end
