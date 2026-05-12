#
# @lc app=leetcode id=1029 lang=python3
#
# [1029] Two City Scheduling
#
# https://leetcode.com/problems/two-city-scheduling/description/
#
# algorithms
# Medium (68.50%)
# Likes:    4884
# Dislikes: 367
# Total Accepted:    287.8K
# Total Submissions: 420K
# Testcase Example:  '[[10,20],[30,200],[400,50],[30,20]]'
#
# A company is planning to interview 2n people. Given the array costs where
# costs[i] = [aCosti, bCosti], the cost of flying the i^th person to city a is
# aCosti, and the cost of flying the i^th person to city b is bCosti.
# 
# Return the minimum cost to fly every person to a city such that exactly n
# people arrive in each city.
# 
# 
# Example 1:
# 
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
# 
# Example 2:
# 
# 
# Input: costs = [[259,770],[448,54],[926,667],[184,139],[840,118],[577,469]]
# Output: 1859
# 
# 
# Example 3:
# 
# 
# Input: costs =
# [[515,563],[451,713],[537,709],[343,819],[855,779],[457,60],[650,359],[631,42]]
# Output: 3086
# 
# 
# 
# Constraints:
# 
# 
# 2 * n == costs.length
# 2 <= costs.length <= 100
# costs.length is even.
# 1 <= aCosti, bCosti <= 1000
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def twoCitySchedCost(self, costs: List[List[int]]) -> int:
        costs.sort(key=lambda cost: cost[0] - cost[1])
        half = len(costs) // 2

        return sum(costs[i][0] for i in range(half)) + sum(
            costs[i][1] for i in range(half, len(costs))
        )
# @lc code=end

"""
Interview Explanation

Core idea:
Think of sending everyone to city B first. Sending person i to city A instead
changes the cost by aCost - bCost. We need choose exactly n people with the
smallest such changes.

Algorithm:
1. Sort people by (cost to A - cost to B).
2. Send the first half to A; these are the people for whom A is most favorable.
3. Send the remaining half to B.
4. Sum the chosen costs.

Data structure choice:
A sorted list is enough because each person's decision has one independent
exchange value. Dynamic programming would work but is unnecessary for the
fixed "exactly half" constraint.

Correctness:
Suppose a person sent to B has a smaller A-B difference than a person sent to
A. Swapping their destinations would not increase the total cost, and would
usually decrease it. Therefore in an optimal solution, all A-assigned people
come before all B-assigned people in sorted difference order. The algorithm
constructs exactly that assignment.

Complexity:
Sorting costs O(n log n) for 2n people. Extra space is O(1) beyond the sort's
internal storage.

Tests and edge cases:
- Two people only: cheaper assignment by difference is selected.
- Equal differences: either order has the same total cost.
- Very large individual costs still fit easily in Python integers.
"""
