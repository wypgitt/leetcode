#
# @lc app=leetcode id=91 lang=python3
#
# [91] Decode Ways
#
# https://leetcode.com/problems/decode-ways/description/
#
# algorithms
# Medium (37.94%)
# Likes:    12917
# Dislikes: 4616
# Total Accepted:    1.7M
# Total Submissions: 4.4M
# Testcase Example:  '"12"'
#
# You have intercepted a secret message encoded as a string of numbers. The
# message is decoded via the following mapping:
# 
# "1" -> 'A'
# "2" -> 'B'
# ...
# "25" -> 'Y'
# "26" -> 'Z'
# 
# However, while decoding the message, you realize that there are many
# different ways you can decode the message because some codes are contained in
# other codes ("2" and "5" vs "25").
# 
# For example, "11106" can be decoded into:
# 
# 
# "AAJF" with the grouping (1, 1, 10, 6)
# "KJF" with the grouping (11, 10, 6)
# The grouping (1, 11, 06) is invalid because "06" is not a valid code (only
# "6" is valid).
# 
# 
# Note: there may be strings that are impossible to decode.
# 
# Given a string s containing only digits, return the number of ways to decode
# it. If the entire string cannot be decoded in any valid way, return 0.
# 
# The test cases are generated so that the answer fits in a 32-bit integer.
# 
# 
# Example 1:
# 
# 
# Input: s = "12"
# 
# Output: 2
# 
# Explanation:
# 
# "12" could be decoded as "AB" (1 2) or "L" (12).
# 
# 
# Example 2:
# 
# 
# Input: s = "226"
# 
# Output: 3
# 
# Explanation:
# 
# "226" could be decoded as "BZ" (2 26), "VF" (22 6), or "BBF" (2 2 6).
# 
# 
# Example 3:
# 
# 
# Input: s = "06"
# 
# Output: 0
# 
# Explanation:
# 
# "06" cannot be mapped to "F" because of the leading zero ("6" is different
# from "06"). In this case, the string is not a valid encoding, so return
# 0.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 100
# s contains only digits and may contain leading zero(s).
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def numDecodings(self, s: str) -> int:
        """
        Interview explanation:
        Decode counts depend on the previous one or two characters. Let dp[i]
        mean ways to decode s[:i]. A one-digit decode is valid for '1'..'9'; a
        two-digit decode is valid for '10'..'26'. Keep only the previous two DP
        values for O(1) space.

        Edge cases and tests:
        - Leading zero returns 0.
        - '10' and '20' are valid only as two-digit decodes.
        - '06' is invalid because '06' is not a letter.

        Complexity: O(n) time, O(1) space.
        """
        if not s or s[0] == '0':
            return 0

        two_back = 1
        one_back = 1
        for i in range(1, len(s)):
            cur = 0
            if s[i] != '0':
                cur += one_back
            two_digit = int(s[i - 1:i + 1])
            if 10 <= two_digit <= 26:
                cur += two_back
            two_back, one_back = one_back, cur

        return one_back
# @lc code=end


