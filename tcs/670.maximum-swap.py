#
# @lc app=leetcode id=670 lang=python3
#
# [670] Maximum Swap
#
# https://leetcode.com/problems/maximum-swap/description/
#
# algorithms
# Medium (52.08%)
# Likes:    4312
# Dislikes: 276
# Total Accepted:    520K
# Total Submissions: 999K
# Testcase Example:  "2736"
#
# You are given an integer num. You can swap two digits at most once to get the
# maximum valued number.
#
# Return the maximum valued number you can get.
#
# Example 1:
#
# Input: num = 2736
# Output: 7236
# Explanation: Swap the number 2 and the number 7.
#
# Example 2:
#
# Input: num = 9973
# Output: 9973
# Explanation: No swap.
#
# Constraints:
#
# 0 <= num <= 10^8
#

# @lc code=start
class Solution:
    def maximumSwap(self, num: int) -> int:
        """
        Interview explanation:
        At most one digit swap to maximize the number. Improve the leftmost
        digit possible by swapping with the rightmost occurrence of a larger
        digit to its right.

        Algorithm:
        - Record last index of each digit 0-9.
        - For i from left: for d from 9 down to digits[i]+1, if last[d] > i, swap.

        Complexity: O(d) time/space (d = digit count).
        """
        digits = list(str(num))
        last = {int(d): i for i, d in enumerate(digits)}
        for i, ch in enumerate(digits):
            cur = int(ch)
            for d in range(9, cur, -1):
                if last.get(d, -1) > i:
                    j = last[d]
                    digits[i], digits[j] = digits[j], digits[i]
                    return int("".join(digits))
        return num
# @lc code=end
