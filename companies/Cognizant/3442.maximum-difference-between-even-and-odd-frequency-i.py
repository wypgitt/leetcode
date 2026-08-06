#
# @lc app=leetcode id=3442 lang=python3
#
# [3442] Maximum Difference Between Even and Odd Frequency I
#
# https://leetcode.com/problems/maximum-difference-between-even-and-odd-frequency-i/description/
#
# algorithms
# Easy (60.75%)
# Likes:    401
# Dislikes: 71
# Total Accepted:    184.9K
# Total Submissions: 304.4K
# Testcase Example:  "\"aaaaabbc\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# Your task is to find the maximum difference diff = freq(a_1) - freq(a_2)
# between the frequency of characters a_1 and a_2 in the string such that:
#
# a_1 has an odd frequency in the string.
#
# a_2 has an even frequency in the string.
#
# Return this maximum difference.
#
# Example 1:
#
# Input: s = "aaaaabbc"
#
# Output: 3
#
# Explanation:
#
# The character 'a' has an odd frequency of 5, and 'b' has an even
# frequency of 2.
#
# The maximum difference is 5 - 2 = 3.
#
# Example 2:
#
# Input: s = "abcabcab"
#
# Output: 1
#
# Explanation:
#
# The character 'a' has an odd frequency of 3, and 'c' has an even
# frequency of 2.
#
# The maximum difference is 3 - 2 = 1.
#
# Constraints:
#
# 3 <= s.length <= 100
#
# s consists only of lowercase English letters.
#
# s contains at least one character with an odd frequency and one with an
# even frequency.
#

# @lc code=start

from collections import Counter


class Solution:
    def maxDifference(self, s: str) -> int:
        """
        Interview explanation:
        Maximize freq(odd-char) - freq(even-char) over the whole string.

        Algorithm:
        - Count frequencies; take max among odd counts minus min among even counts.

        Complexity: O(n) time, O(1) space (26 letters).

        Alternate: scan Counter values once collecting max_odd / min_even.
        """
        freq = Counter(s)
        max_odd = max(v for v in freq.values() if v % 2 == 1)
        min_even = min(v for v in freq.values() if v % 2 == 0)
        return max_odd - min_even
# @lc code=end
