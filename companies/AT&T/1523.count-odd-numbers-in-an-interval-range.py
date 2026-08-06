#
# @lc app=leetcode id=1523 lang=python3
#
# [1523] Count Odd Numbers in an Interval Range
#
# https://leetcode.com/problems/count-odd-numbers-in-an-interval-range/description/
#
# algorithms
# Easy (54.75%)
# Likes:    3148
# Dislikes: 182
# Total Accepted:    577K
# Total Submissions: 1.1M
# Testcase Example:  "3"
#
# Given two non-negative integers low and high. Return the count of odd numbers
# between low and high (inclusive).
#
# Example 1:
#
# Input: low = 3, high = 7
# Output: 3
# Explanation: The odd numbers between 3 and 7 are [3,5,7].
#
# Example 2:
#
# Input: low = 8, high = 10
# Output: 1
# Explanation: The odd numbers between 8 and 10 are [9].
#
# Constraints:
#
# 0 <= low <= high <= 10^9
#

# @lc code=start
class Solution:
    def countOdds(self, low: int, high: int) -> int:
        """
        Interview explanation:
        Count odds in [low, high]. Math: numbers = high-low+1; about half are
        odd. Formula: (high+1)//2 - low//2.

        Algorithm:
        - return (high + 1) // 2 - low // 2.

        Complexity: O(1).
        """
        return (high + 1) // 2 - low // 2

    def countOdds_loop(self, low: int, high: int) -> int:
        """
        Interview explanation:
        Alternate: if low even bump to next odd; then count odds by step 2.

        Algorithm:
        - if low%2==0: low+=1; return 0 if low>high else (high-low)//2+1.

        Complexity: O(1).
        """
        if low % 2 == 0:
            low += 1
        if low > high:
            return 0
        return (high - low) // 2 + 1
# @lc code=end
