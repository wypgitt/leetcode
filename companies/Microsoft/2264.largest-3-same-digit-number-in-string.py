#
# @lc app=leetcode id=2264 lang=python3
#
# [2264] Largest 3-Same-Digit Number in String
#
# https://leetcode.com/problems/largest-3-same-digit-number-in-string/description/
#
# algorithms
# Easy (72.66%)
# Likes:    1397
# Dislikes: 55
# Total Accepted:    331.7K
# Total Submissions: 456.5K
# Testcase Example:  "\"6777133339\""
#
# You are given a string num representing a large integer. An integer is good if
# it meets the following conditions:
#
#
# It is a substring of num with length 3.
#
#
# It consists of only one unique digit.
#
# Return the maximum good integer as a string or an empty string "" if no such
# integer exists.
#
# Note:
#
#
# A substring is a contiguous sequence of characters within a string.
#
#
# There may be leading zeroes in num or a good integer.
#
#
#
# Example 1:
#
# Input: num = "6777133339"
# Output: "777"
# Explanation: There are two distinct good integers: "777" and "333".
# "777" is the largest, so we return "777".
#
# Example 2:
#
# Input: num = "2300019"
# Output: "000"
# Explanation: "000" is the only good integer.
#
# Example 3:
#
# Input: num = "42352338"
# Output: ""
# Explanation: No substring of length 3 consists of only one unique digit.
# Therefore, there are no good integers.
#
#
#
# Constraints:
#
#
# 3 <= num.length <= 1000
#
#
# num only consists of digits.
#

# @lc code=start
class Solution:
    def largestGoodInteger(self, num: str) -> str:
        """
        Interview explanation:
        Largest substring of length 3 with identical digits, or "".

        Algorithm:
        - Scan for triples; keep max lexicographic among digit*3.

        Complexity: O(n) time, O(1) space.
        """
        ans = ""
        for i in range(len(num) - 2):
            if num[i] == num[i + 1] == num[i + 2]:
                ans = max(ans, num[i : i + 3])
        return ans
# @lc code=end
