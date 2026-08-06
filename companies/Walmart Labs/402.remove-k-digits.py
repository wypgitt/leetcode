#
# @lc app=leetcode id=402 lang=python3
#
# [402] Remove K Digits
#
# https://leetcode.com/problems/remove-k-digits/description/
#
# algorithms
# Medium (37.41%)
# Likes:    10753
# Dislikes: 557
# Total Accepted:    783K
# Total Submissions: 2.1M
# Testcase Example:  "\"1432219\""
#
# Given string num representing a non-negative integer num, and an integer k,
# return the smallest possible integer after removing k digits from num.
#
# Example 1:
#
# Input: num = "1432219", k = 3
# Output: "1219"
# Explanation: Remove the three digits 4, 3, and 2 to form the new number 1219
# which is the smallest.
#
# Example 2:
#
# Input: num = "10200", k = 1
# Output: "200"
# Explanation: Remove the leading 1 and the number is 200. Note that the output
# must not contain leading zeroes.
#
# Example 3:
#
# Input: num = "10", k = 2
# Output: "0"
# Explanation: Remove all the digits from the number and it is left with
# nothing which is 0.
#
# Constraints:
#
# 1 <= k <= num.length <= 10^5
#
# num consists of only digits.
#
# num does not have any leading zeros except for the zero itself.
#

# @lc code=start

class Solution:
    def removeKdigits(self, num: str, k: int) -> str:
        """
        Interview explanation:
        Monotonic non-decreasing stack of digits: greedily remove peaks so the
        remaining digit sequence is the smallest possible after k deletions.

        Algorithm:
        - For each digit, while k>0 and stack top > digit, pop (delete peak).
        - Append digit; after scan, pop remaining k digits from the end.
        - Strip leading zeros; return "0" if empty.

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        for d in num:
            while k and stack and stack[-1] > d:
                stack.pop()
                k -= 1
            stack.append(d)
        if k:
            stack = stack[:-k]
        return "".join(stack).lstrip("0") or "0"
# @lc code=end
