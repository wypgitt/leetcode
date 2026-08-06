#
# @lc app=leetcode id=409 lang=python3
#
# [409] Longest Palindrome
#
# https://leetcode.com/problems/longest-palindrome/description/
#
# algorithms
# Easy (56.15%)
# Likes:    6450
# Dislikes: 456
# Total Accepted:    1.1M
# Total Submissions: 2.0M
# Testcase Example:  "\"abccccdd\""
#
# Given a string s which consists of lowercase or uppercase letters, return the
# length of the longest palindrome that can be built with those letters.
#
# Letters are case sensitive, for example, "Aa" is not considered a palindrome.
#
# Example 1:
#
# Input: s = "abccccdd"
# Output: 7
# Explanation: One longest palindrome that can be built is "dccaccd", whose
# length is 7.
#
# Example 2:
#
# Input: s = "a"
# Output: 1
# Explanation: The longest palindrome that can be built is "a", whose length is
# 1.
#
# Constraints:
#
# 1 <= s.length <= 2000
#
# s consists of lowercase and/or uppercase English letters only.
#

# @lc code=start

from collections import Counter


class Solution:
    def longestPalindrome(self, s: str) -> int:
        """
        Interview explanation:
        In a palindrome, all chars can form pairs; at most one char can be odd
        (center). Sum even counts + 1 if any odd count exists.

        Algorithm:
        - Count frequencies; ans = sum(c//2*2); if any odd, ans += 1.

        Complexity: O(n) time, O(1) space (alphabet-sized map).
        """
        counts = Counter(s)
        ans = 0
        odd = False
        for c in counts.values():
            ans += c // 2 * 2
            if c % 2:
                odd = True
        return ans + (1 if odd else 0)
# @lc code=end
