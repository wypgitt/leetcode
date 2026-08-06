#
# @lc app=leetcode id=2370 lang=python3
#
# [2370] Longest Ideal Subsequence
#
# https://leetcode.com/problems/longest-ideal-subsequence/description/
#
# algorithms
# Medium (46.60%)
# Likes:    1542
# Dislikes: 83
# Total Accepted:    126K
# Total Submissions: 270.5K
# Testcase Example:  "\"acfgbd\"\n2"
#
# You are given a string s consisting of lowercase letters and an integer k. We
# call a string t ideal if the following conditions are satisfied:
#
#
# t is a subsequence of the string s.
#
#
# The absolute difference in the alphabet order of every two adjacent letters in
# t is less than or equal to k.
#
# Return the length of the longest ideal string.
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
# Note that the alphabet order is not cyclic. For example, the absolute
# difference in the alphabet order of 'a' and 'z' is 25, not 1.
#
#
#
# Example 1:
#
# Input: s = "acfgbd", k = 2
# Output: 4
# Explanation: The longest ideal string is "acbd". The length of this string is
# 4, so 4 is returned.
# Note that "acfgbd" is not ideal because 'c' and 'f' have a difference of 3 in
# alphabet order.
#
# Example 2:
#
# Input: s = "abcd", k = 3
# Output: 4
# Explanation: The longest ideal string is "abcd". The length of this string is
# 4, so 4 is returned.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# 0 <= k <= 25
#
#
# s consists of lowercase English letters.
#

# @lc code=start

class Solution:
    def longestIdealString(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Longest subsequence where consecutive chars differ by at most k in
        alphabet distance.

        Algorithm:
        - DP over alphabet: dp[c] = longest ending with char c. For each char,
          take max(dp[c-k..c+k])+1.

        Complexity: O(n * 26) time, O(26) space.
        """
        dp = [0] * 26
        for ch in s:
            i = ord(ch) - 97
            best = 0
            for j in range(max(0, i - k), min(25, i + k) + 1):
                best = max(best, dp[j])
            dp[i] = best + 1
        return max(dp)
# @lc code=end
