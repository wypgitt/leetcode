#
# @lc app=leetcode id=1029 lang=python3
#
# [1029] Two City Scheduling
#
# https://leetcode.com/problems/two-city-scheduling/description/
#
# algorithms
# Medium (68.8%)
# Likes:    4909
# Dislikes: 367
# Total Accepted:    294K
# Total Submissions: 428K
# Testcase Example:  "[[10,20],[30,200],[400,50],[30,20]]"
#
# A company is planning to interview 2n people. Given the array costs where
# costs[i] = [aCost_i, bCost_i], the cost of flying the i^th person to city a
# is aCost_i, and the cost of flying the i^th person to city b is bCost_i.
#
# Return the minimum cost to fly every person to a city such that exactly n
# people arrive in each city.
#
# Example 1:
#
# Input: costs = [[10,20],[30,200],[400,50],[30,20]]
# Output: 110
# Explanation:
# The first person goes to city A for a cost of 10.
# The second person goes to city A for a cost of 30.
# The third person goes to city B for a cost of 50.
# The fourth person goes to city B for a cost of 20.
#
# The total minimum cost is 10 + 30 + 50 + 20 = 110 to have half the people
# interviewing in each city.
#
# Example 2:
#
# Input: costs = [[259,770],[448,54],[926,667],[184,139],[840,118],[577,469]]
# Output: 1859
#
# Example 3:
#
# Input: costs =
# [[515,563],[451,713],[537,709],[343,819],[855,779],[457,60],[650,359],[631,42]]
# Output: 3086
#
# Constraints:
#
# 2 * n == costs.length
#
# 2 <= costs.length <= 100
#
# costs.length is even.
#
# 1 <= aCost_i, bCost_i <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def twoCitySchedCost(self, costs: List[List[int]]) -> int:
        """
        Interview explanation:
        Send all to A first, then choose n people with largest (A-B) savings
        (i.e. smallest costA-costB) to send to B instead — sort by costA-costB.

        Algorithm:
        - Sort by a-b ascending
        - First n go to A, last n go to B; sum costs

        Complexity: O(n log n) time, O(n) space.
        """
        costs.sort(key=lambda x: x[0] - x[1])
        n = len(costs) // 2
        return sum(costs[i][0] for i in range(n)) + sum(costs[i][1] for i in range(n, 2 * n))

    def twoCitySchedCost_heap(self, costs: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: total if all go to A, then pick n largest (a-b) refunds via
        heap to switch to B.

        Algorithm:
        - total = sum(a); refunds = a-b; take n largest refunds subtract

        Complexity: O(n log n) time, O(n) space.
        """
        import heapq

        n = len(costs) // 2
        total = sum(a for a, _ in costs)
        refunds = [a - b for a, b in costs]
        # subtract the n largest (a-b) = send those to B
        largest = heapq.nlargest(n, refunds)
        return total - sum(largest)
# @lc code=end
