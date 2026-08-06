#
# @lc app=leetcode id=2311 lang=python3
#
# [2311] Longest Binary Subsequence Less Than or Equal to K
#
# https://leetcode.com/problems/longest-binary-subsequence-less-than-or-equal-to-k/description/
#
# algorithms
# Medium (52.74%)
# Likes:    1150
# Dislikes: 79
# Total Accepted:    112.2K
# Total Submissions: 212.8K
# Testcase Example:  "\"1001010\"\n5"
#
# You are given a binary string s and a positive integer k.
#
# Return the length of the longest subsequence of s that makes up a binary
# number less than or equal to k.
#
# Note:
#
#
# The subsequence can contain leading zeroes.
#
#
# The empty string is considered to be equal to 0.
#
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
#
#
# Example 1:
#
# Input: s = "1001010", k = 5
# Output: 5
# Explanation: The longest subsequence of s that makes up a binary number less
# than or equal to 5 is "00010", as this number is equal to 2 in decimal.
# Note that "00100" and "00101" are also possible, which are equal to 4 and 5 in
# decimal, respectively.
# The length of this subsequence is 5, so 5 is returned.
#
# Example 2:
#
# Input: s = "00101001", k = 1
# Output: 6
# Explanation: "000001" is the longest subsequence of s that makes up a binary
# number less than or equal to 1, as this number is equal to 1 in decimal.
# The length of this subsequence is 6, so 6 is returned.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 1000
#
#
# s[i] is either '0' or '1'.
#
#
# 1 <= k <= 10^9
#

# @lc code=start
class Solution:
    def longestSubsequence(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Longest subsequence of binary string s whose integer value <= k.

        Algorithm:
        - Build from the LSB (right): always take '0'; take '1' when
          val + 2^(current_length) <= k. Bit weight equals current subsequence
          length when appending as the new MSB... actually appending as next
          higher bit at index = current length.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        val = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == '0':
                ans += 1
            else:
                if ans > 30:
                    continue
                add = 1 << ans
                if val + add <= k:
                    val += add
                    ans += 1
        return ans
# @lc code=end
