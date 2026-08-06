#
# @lc app=leetcode id=2554 lang=python3
#
# [2554] Maximum Number of Integers to Choose From a Range I
#
# https://leetcode.com/problems/maximum-number-of-integers-to-choose-from-a-range-i/description/
#
# algorithms
# Medium (67.99%)
# Likes:    834
# Dislikes: 57
# Total Accepted:    171.7K
# Total Submissions: 252.6K
# Testcase Example:  "[1,6,5]\n5\n6"
#
# You are given an integer array banned and two integers n and maxSum. You are
# choosing some number of integers following the below rules:
#
#
# The chosen integers have to be in the range [1, n].
#
#
# Each integer can be chosen at most once.
#
#
# The chosen integers should not be in the array banned.
#
#
# The sum of the chosen integers should not exceed maxSum.
#
# Return the maximum number of integers you can choose following the mentioned
# rules.
#
#
#
# Example 1:
#
# Input: banned = [1,6,5], n = 5, maxSum = 6
# Output: 2
# Explanation: You can choose the integers 2 and 4.
# 2 and 4 are from the range [1, 5], both did not appear in banned, and their
# sum is 6, which did not exceed maxSum.
#
# Example 2:
#
# Input: banned = [1,2,3,4,5,6,7], n = 8, maxSum = 1
# Output: 0
# Explanation: You cannot choose any integer while following the mentioned
# conditions.
#
# Example 3:
#
# Input: banned = [11], n = 7, maxSum = 50
# Output: 7
# Explanation: You can choose the integers 1, 2, 3, 4, 5, 6, and 7.
# They are from the range [1, 7], all did not appear in banned, and their sum is
# 28, which did not exceed maxSum.
#
#
#
# Constraints:
#
#
# 1 <= banned.length <= 10^4
#
#
# 1 <= banned[i], n <= 10^4
#
#
# 1 <= maxSum <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxCount(self, banned: List[int], n: int, maxSum: int) -> int:
        """
        Interview explanation:
        Choose max count of distinct integers in [1,n] not banned with sum <= maxSum.
        Prefer smallest available numbers greedily.

        Algorithm:
        - Put banned into a set; iterate i=1..n, take if not banned and sum allows.

        Complexity: O(n + |banned|) time, O(|banned|) space.
        """
        ban = set(banned)
        total = 0
        cnt = 0
        for i in range(1, n + 1):
            if i in ban:
                continue
            if total + i > maxSum:
                break
            total += i
            cnt += 1
        return cnt
# @lc code=end
