#
# @lc app=leetcode id=2609 lang=python3
#
# [2609] Find the Longest Balanced Substring of a Binary String
#
# https://leetcode.com/problems/find-the-longest-balanced-substring-of-a-binary-string/description/
#
# algorithms
# Easy (46.86%)
# Likes:    401
# Dislikes: 32
# Total Accepted:    40.6K
# Total Submissions: 86.7K
# Testcase Example:  "\"01000111\""
#
# You are given a binary string s consisting only of zeroes and ones.
#
# A substring of s is considered balanced if all zeroes are before ones and the
# number of zeroes is equal to the number of ones inside the substring. Notice
# that the empty substring is considered a balanced substring.
#
# Return the length of the longest balanced substring of s.
#
# A substring is a contiguous sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "01000111"
# Output: 6
# Explanation: The longest balanced substring is "000111", which has length 6.
#
# Example 2:
#
# Input: s = "00111"
# Output: 4
# Explanation: The longest balanced substring is "0011", which has length 4.
#
# Example 3:
#
# Input: s = "111"
# Output: 0
# Explanation: There is no balanced substring except the empty substring, so the
# answer is 0.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 50
#
#
# '0' <= s[i] <= '1'
#

# @lc code=start
class Solution:
    def findTheLongestBalancedSubstring(self, s: str) -> int:
        """
        Interview explanation:
        A balanced substring is zeros followed by the same count of ones.
        Find the longest such substring length.

        Algorithm:
        - Scan left to right tracking consecutive zero then one runs;
          whenever a '1' run ends (or string ends), update ans with
          2 * min(zeros, ones). Reset on pattern breaks.

        Complexity: O(n) time, O(1) space.
        """
        ans = zeros = ones = 0
        i, n = 0, len(s)
        while i < n:
            zeros = 0
            while i < n and s[i] == "0":
                zeros += 1
                i += 1
            ones = 0
            while i < n and s[i] == "1":
                ones += 1
                i += 1
            ans = max(ans, 2 * min(zeros, ones))
        return ans
# @lc code=end
