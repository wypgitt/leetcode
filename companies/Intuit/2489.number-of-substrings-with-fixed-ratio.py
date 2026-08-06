#
# @lc app=leetcode id=2489 lang=python3
#
# [2489] Number of Substrings With Fixed Ratio
#
# https://leetcode.com/problems/number-of-substrings-with-fixed-ratio/description/
#
# algorithms
# Medium (56.98%)
# Likes:    55
# Dislikes: 3
# Total Accepted:    1.8K
# Total Submissions: 3.1K
# Testcase Example:  "\"0110011\"\n1\n2"
#
#
# You are given a binary string s, and two integers num1 and num2. num1
# and num2 are coprime numbers.
#
# A ratio substring is a substring of s where the ratio between the number
# of 0's and the number of 1's in the substring is exactly num1 : num2.
#
# For example, if num1 = 2 and num2 = 3, then "01011" and "1110000111" are
# ratio substrings, while "11000" is not.
#
# Return the number of non-empty ratio substrings of s.
#
# Note that:
#
# A substring is a contiguous sequence of characters within a string.
#
# Two values x and y are coprime if gcd(x, y) == 1 where gcd(x, y) is the
# greatest common divisor of x and y.
#
# Example 1:
#
# Input: s = "0110011", num1 = 1, num2 = 2
# Output: 4
# Explanation: There exist 4 non-empty ratio substrings.
# - The substring s[0..2]: "0110011". It contains one 0 and two 1's. The
# ratio is 1 : 2.
# - The substring s[1..4]: "0110011". It contains one 0 and two 1's. The
# ratio is 1 : 2.
# - The substring s[4..6]: "0110011". It contains one 0 and two 1's. The
# ratio is 1 : 2.
# - The substring s[1..6]: "0110011". It contains two 0's and four 1's.
# The ratio is 2 : 4 == 1 : 2.
# It can be shown that there are no more ratio substrings.
#
# Example 2:
#
# Input: s = "10101", num1 = 3, num2 = 1
# Output: 0
# Explanation: There is no ratio substrings of s. We return 0.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 1 <= num1, num2 <= s.length
#
# num1 and num2 are coprime integers.
#
# @lc code=start
from collections import Counter


class Solution:
    def fixedRatio(self, s: str, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Premium. Count substrings where (#zeros):( #ones) == num1:num2
        (num1,num2 coprime).

        Algorithm:
        - Prefix: ones*num1 - zeros*num2 equal at ends of good substrings;
          hash counts of that key.

        Complexity: O(n) time, O(n) space.
        """
        n0 = n1 = ans = 0
        cnt = Counter({0: 1})
        for c in s:
            n0 += c == "0"
            n1 += c == "1"
            x = n1 * num1 - n0 * num2
            ans += cnt[x]
            cnt[x] += 1
        return ans
# @lc code=end

