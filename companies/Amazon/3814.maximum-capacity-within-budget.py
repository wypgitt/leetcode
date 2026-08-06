#
# @lc app=leetcode id=3814 lang=python3
#
# [3814] Maximum Capacity Within Budget
#
# https://leetcode.com/problems/maximum-capacity-within-budget/description/
#
# algorithms
# Medium (20.65%)
# Likes:    200
# Dislikes: 17
# Total Accepted:    20.5K
# Total Submissions: 99.4K
# Testcase Example:  "[4,8,5,3]\n[1,5,2,7]\n8"
#
#
# You are given two integer arrays costs and capacity, both of length n,
# where costs[i] represents the purchase cost of the i^th machine and
# capacity[i] represents its performance capacity.
#
# You are also given an integer budget.
#
# You may select at most two distinct machines such that the total cost of
# the selected machines is strictly less than budget.
#
# Return the maximum achievable total capacity of the selected machines.
#
# Example 1:
#
# Input: costs = [4,8,5,3], capacity = [1,5,2,7], budget = 8
#
# Output: 8
#
# Explanation:
#
# Choose two machines with costs[0] = 4 and costs[3] = 3.
#
# The total cost is 4 + 3 = 7, which is strictly less than budget = 8.
#
# The maximum total capacity is capacity[0] + capacity[3] = 1 + 7 = 8.
#
# Example 2:
#
# Input: costs = [3,5,7,4], capacity = [2,4,3,6], budget = 7
#
# Output: 6
#
# Explanation:
#
# Choose one machine with costs[3] = 4.
#
# The total cost is 4, which is strictly less than budget = 7.
#
# The maximum total capacity is capacity[3] = 6.
#
# Example 3:
#
# Input: costs = [2,2,2], capacity = [3,5,4], budget = 5
#
# Output: 9
#
# Explanation:
#
# Choose two machines with costs[1] = 2 and costs[2] = 2.
#
# The total cost is 2 + 2 = 4, which is strictly less than budget = 5.
#
# The maximum total capacity is capacity[1] + capacity[2] = 5 + 4 = 9.
#
# Constraints:
#
# 1 <= n == costs.length == capacity.length <= 10^5
#
# 1 <= costs[i], capacity[i] <= 10^5
#
# 1 <= budget <= 2 * 10^5
#

# @lc code=start

from typing import List

from sortedcontainers import SortedList


class Solution:
    def maxCapacity(
        self, costs: List[int], capacity: List[int], budget: int
    ) -> int:
        """
        Interview explanation:
        Pick at most two machines with total cost < budget maximizing total
        capacity. Sort by cost and use two pointers plus an ordered multiset
        of partner capacities.

        Algorithm:
        - Keep machines with cost < budget; ans starts as best single.
        - Sort by cost. Maintain SortedList of (capacity, index) for candidates
          j that can pair with current i (cost_i + cost_j < budget).
        - Sweep i from left, shrink j from right, take max partner capacity.

        Complexity: O(n log n) time, O(n) space.
        """
        arr = [(a, b) for a, b in zip(costs, capacity) if a < budget]
        if not arr:
            return 0
        arr.sort()
        remain: SortedList = SortedList()
        for i, (_, b) in enumerate(arr):
            remain.add((b, i))
        i, j = 0, len(arr) - 1
        ans = remain[-1][0]
        while i < j:
            remain.discard((arr[i][1], i))
            while i < j and arr[i][0] + arr[j][0] >= budget:
                remain.discard((arr[j][1], j))
                j -= 1
            if remain:
                ans = max(ans, arr[i][1] + remain[-1][0])
            i += 1
        return ans
# @lc code=end
