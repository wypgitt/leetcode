#
# @lc app=leetcode id=1478 lang=python3
#
# [1478] Allocate Mailboxes
#
# https://leetcode.com/problems/allocate-mailboxes/description/
#
# algorithms
# Hard (56.84%)
# Likes:    1191
# Dislikes: 23
# Total Accepted:    35.4K
# Total Submissions: 62.3K
# Testcase Example:  "[1,4,8,10,20]"
#
# Given the array houses where houses[i] is the location of the i^th house
# along a street and an integer k, allocate k mailboxes in the street.
#
# Return the minimum total distance between each house and its nearest mailbox.
#
# The test cases are generated so that the answer fits in a 32-bit integer.
#
# Example 1:
#
# Input: houses = [1,4,8,10,20], k = 3
# Output: 5
# Explanation: Allocate mailboxes in position 3, 9 and 20.
# Minimum total distance from each houses to nearest mailboxes is |3-1| + |4-3|
# + |9-8| + |10-9| + |20-20| = 5
#
# Example 2:
#
# Input: houses = [2,3,5,12,18], k = 2
# Output: 9
# Explanation: Allocate mailboxes in position 3 and 14.
# Minimum total distance from each houses to nearest mailboxes is |2-3| + |3-3|
# + |5-3| + |12-14| + |18-14| = 9.
#
# Constraints:
#
# 1 <= k <= houses.length <= 100
#
# 1 <= houses[i] <= 10^4
#
# All the integers of houses are unique.
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def minDistance(self, houses: List[int], k: int) -> int:
        """
        Interview explanation:
        Place k mailboxes on number line to minimize sum of distances from each
        house to nearest mailbox. Optimal mailbox for a contiguous group is at
        the median. DP: cost(i,j) = cost of covering houses[i..j] with one
        mailbox; dp[j][mailboxes].

        Algorithm:
        - Sort houses; cost[i][j] = sum |houses[t]-median|;
          dp(i,k)=min over t of cost[i][t]+dp(t+1,k-1).

        Complexity: O(n^2 * k + n^2) time, O(n^2 + nk) space.
        """
        houses = sorted(houses)
        n = len(houses)
        cost = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                mid = houses[(i + j) // 2]
                cost[i][j] = sum(abs(houses[t] - mid) for t in range(i, j + 1))

        @lru_cache(None)
        def dp(i, left):
            if left == 1:
                return cost[i][n - 1]
            if i == n:
                return 0
            best = 10**15
            for j in range(i, n - left + 1):
                best = min(best, cost[i][j] + dp(j + 1, left - 1))
            return best

        return dp(0, k)
# @lc code=end
