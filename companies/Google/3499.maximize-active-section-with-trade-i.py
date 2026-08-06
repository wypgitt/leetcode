#
# @lc app=leetcode id=3499 lang=python3
#
# [3499] Maximize Active Section with Trade I
#
# https://leetcode.com/problems/maximize-active-section-with-trade-i/description/
#
# algorithms
# Medium (60.94%)
# Likes:    348
# Dislikes: 73
# Total Accepted:    111.8K
# Total Submissions: 183.4K
# Testcase Example:  "\"01\""
#
#
# You are given a binary string s of length n, where:
#
# '1' represents an active section.
#
# '0' represents an inactive section.
#
# You can perform at most one trade to maximize the number of active
# sections in s. In a trade, you:
#
# Convert a contiguous block of '1's that is surrounded by '0's to all
# '0's.
#
# Afterward, convert a contiguous block of '0's that is surrounded by '1's
# to all '1's.
#
# Return the maximum number of active sections in s after making the
# optimal trade.
#
# Note: Treat s as if it is augmented with a '1' at both ends, forming t =
# '1' + s + '1'. The augmented '1's do not contribute to the final count.
#
# Example 1:
#
# Input: s = "01"
#
# Output: 1
#
# Explanation:
#
# Because there is no block of '1's surrounded by '0's, no valid trade is
# possible. The maximum number of active sections is 1.
#
# Example 2:
#
# Input: s = "0100"
#
# Output: 4
#
# Explanation:
#
# String "0100" → Augmented to "101001".
#
# Choose "0100", convert "101001" → "100001" → "111111".
#
# The final string without augmentation is "1111". The maximum number of
# active sections is 4.
#
# Example 3:
#
# Input: s = "1000100"
#
# Output: 7
#
# Explanation:
#
# String "1000100" → Augmented to "110001001".
#
# Choose "000100", convert "110001001" → "110000001" → "111111111".
#
# The final string without augmentation is "1111111". The maximum number
# of active sections is 7.
#
# Example 4:
#
# Input: s = "01010"
#
# Output: 4
#
# Explanation:
#
# String "01010" → Augmented to "1010101".
#
# Choose "010", convert "1010101" → "1000101" → "1111101".
#
# The final string without augmentation is "11110". The maximum number of
# active sections is 4.
#
# Constraints:
#
# 1 <= n == s.length <= 10^5
#
# s[i] is either '0' or '1'
#

# @lc code=start
from itertools import groupby, pairwise


class Solution:
    def maxActiveSectionsAfterTrade(self, s: str) -> int:
        """
        Interview explanation:
        One trade removes a '1'-block surrounded by '0's, then flips a '0'-block
        surrounded by '1's. Net effect: convert two adjacent zero-runs (the
        ones flanking a removed one-run) into ones. Gain = sum of those two
        zero-run lengths.

        Algorithm:
        - Count original ones.
        - Collect zero-run lengths; max gain = max sum of adjacent zero runs.
        - Answer = ones + max_gain (0 if fewer than two zero runs).

        Complexity: O(n) time, O(n) space for run lengths.
        """
        zeros = [len(list(g)) for c, g in groupby(s) if c == '0']
        gain = max((a + b for a, b in pairwise(zeros)), default=0)
        return s.count('1') + gain

    def maxActiveSectionsAfterTrade_two_pointers(self, s: str) -> int:
        """
        Interview explanation:
        Alternate O(1)-extra scan: track previous zero-run while walking groups.

        Algorithm:
        - Two pointers over equal-char segments; update max adjacent zero sum.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        ones = 0
        pre = mx = 0
        i = 0
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            cur = j - i
            if s[i] == '1':
                ones += cur
            else:
                if pre:
                    mx = max(mx, pre + cur)
                pre = cur
            i = j
        return ones + mx
# @lc code=end
