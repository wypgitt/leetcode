#
# @lc app=leetcode id=3662 lang=python3
#
# [3662] Filter Characters by Frequency
#
# https://leetcode.com/problems/filter-characters-by-frequency/description/
#
# algorithms
# Easy (86.53%)
# Likes:    9
# Dislikes: 0
# Total Accepted:    1.6K
# Total Submissions: 1.9K
# Testcase Example:  "\"aadbbcccca\"\n3"
#
#
# You are given a string s consisting of lowercase English letters and an
# integer k.
#
# Your task is to construct a new string that contains only those
# characters from s which appear fewer than k times in the entire string.
# The order of characters in the new string must be the same as their
# order in s.
#
# Return the resulting string. If no characters qualify, return an empty
# string.
#
# Note: Every occurrence of a character that occurs fewer than k times is
# kept.
#
# Example 1:
#
# Input: s = "aadbbcccca", k = 3
#
# Output: "dbb"
#
# Explanation:
#
# Character frequencies in s:
#
# 'a' appears 3 times
#
# 'd' appears 1 time
#
# 'b' appears 2 times
#
# 'c' appears 4 times
#
# Only 'd' and 'b' appear fewer than 3 times. Preserving their order, the
# result is "dbb".
#
# Example 2:
#
# Input: s = "xyz", k = 2
#
# Output: "xyz"
#
# Explanation:
#
# All characters ('x', 'y', 'z') appear exactly once, which is fewer than
# 2. Thus the whole string is returned.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of lowercase English letters.
#
# 1 <= k <= s.length
#

# @lc code=start
import collections


class Solution:
    def filterCharacters(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Keep characters whose global frequency is strictly less than k,
        preserving relative order.

        Algorithm:
        - Count frequencies with a Counter.
        - Build the answer by scanning s once and keeping chars with freq < k.

        Complexity: O(n) time, O(1) space over alphabet size.
        """
        freq = collections.Counter(s)
        return "".join(ch for ch in s if freq[ch] < k)

    def filterCharacters_two_pass(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Alternate: explicit frequency array then filter.

        Algorithm:
        - Tally lowercase counts in an array of size 26.
        - Emit qualifying characters in order.

        Complexity: O(n) time, O(1) space.
        """
        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1
        return "".join(ch for ch in s if cnt[ord(ch) - 97] < k)
# @lc code=end
