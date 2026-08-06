#
# @lc app=leetcode id=1903 lang=python3
#
# [1903] Largest Odd Number in String
#
# https://leetcode.com/problems/largest-odd-number-in-string/description/
#
# algorithms
# Easy (67.91%)
# Likes:    2645
# Dislikes: 150
# Total Accepted:    623K
# Total Submissions: 918K
# Testcase Example:  "\"52\""
#
# You are given a string num, representing a large integer. Return the
# largest-valued odd integer (as a string) that is a non-empty substring of
# num, or an empty string "" if no odd integer exists.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: num = "52"
# Output: "5"
# Explanation: The only non-empty substrings are "5", "2", and "52". "5" is the
# only odd number.
#
# Example 2:
#
# Input: num = "4206"
# Output: ""
# Explanation: There are no odd numbers in "4206".
#
# Example 3:
#
# Input: num = "35427"
# Output: "35427"
# Explanation: "35427" is already an odd number.
#
# Constraints:
#
# 1 <= num.length <= 10^5
#
# num only consists of digits and does not contain any leading zeros.
#

# @lc code=start
class Solution:
    def largestOddNumber(self, num: str) -> str:
        """
        Interview explanation:
        Largest odd-valued substring that is a prefix of num (non-empty) —
        equivalently, longest prefix ending at the rightmost odd digit.

        Algorithm:
        - Scan from right; on first odd digit return num[:i+1]; else "".

        Complexity: O(n) time, O(1) extra space.
        """
        for i in range(len(num) - 1, -1, -1):
            if int(num[i]) % 2 == 1:
                return num[: i + 1]
        return ""
# @lc code=end
