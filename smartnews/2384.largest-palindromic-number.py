#
# @lc app=leetcode id=2384 lang=python3
#
# [2384] Largest Palindromic Number
#
# https://leetcode.com/problems/largest-palindromic-number/description/
#
# algorithms
# Medium (37.32%)
# Likes:    677
# Dislikes: 238
# Total Accepted:    55.8K
# Total Submissions: 149.5K
# Testcase Example:  "\"444947137\""
#
# You are given a string num consisting of digits only.
#
# Return the largest palindromic integer (in the form of a string) that can be
# formed using digits taken from num. It should not contain leading zeroes.
#
# Notes:
#
#
# You do not need to use all the digits of num, but you must use at least one
# digit.
#
#
# The digits can be reordered.
#
#
#
# Example 1:
#
# Input: num = "444947137"
# Output: "7449447"
# Explanation:
# Use the digits "4449477" from "444947137" to form the palindromic integer
# "7449447".
# It can be shown that "7449447" is the largest palindromic integer that can be
# formed.
#
# Example 2:
#
# Input: num = "00009"
# Output: "9"
# Explanation:
# It can be shown that "9" is the largest palindromic integer that can be
# formed.
# Note that the integer returned should not contain leading zeroes.
#
#
#
# Constraints:
#
#
# 1 <= num.length <= 10^5
#
#
# num consists of digits.
#

# @lc code=start

from collections import Counter


class Solution:
    def largestPalindromic(self, num: str) -> str:
        """
        Interview explanation:
        Rearrange digits of num into largest palindromic number (no leading
        zeros unless the answer is "0").

        Algorithm:
        - Count digits; build left half from 9..0 using pairs; pick largest
          leftover single for middle; mirror left. Strip leading zeros carefully.

        Complexity: O(n) time, O(1) space (digit counts).
        """
        cnt = Counter(num)
        left = []
        for d in '9876543210':
            pairs = cnt[d] // 2
            left.append(d * pairs)
            cnt[d] -= pairs * 2
        left_s = ''.join(left).lstrip('0')
        mid = ''
        for d in '9876543210':
            if cnt[d]:
                mid = d
                break
        if not left_s and not mid:
            return '0'
        if not left_s:
            return mid
        return left_s + mid + left_s[::-1]
# @lc code=end
