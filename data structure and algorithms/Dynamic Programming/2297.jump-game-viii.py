#
# @lc app=leetcode id=2297 lang=python3
#
# [2297] Jump Game VIII
#
# https://leetcode.com/problems/jump-game-viii/description/
#
# algorithms
# Medium (45.90%)
# Likes:    175
# Dislikes: 49
# Total Accepted:    8.2K
# Total Submissions: 17.9K
# Testcase Example:  "[3,2,4,4,1]\n[3,7,6,4,2]"
#
#
# You are given a 0-indexed integer array nums of length n. You are
# initially standing at index 0. You can jump from index i to index j
# where i < j if:
#
# nums[i] <= nums[j] and nums[k] < nums[i] for all indexes k in the range
# i < k < j, or
#
# nums[i] > nums[j] and nums[k] >= nums[i] for all indexes k in the range
# i < k < j.
#
# You are also given an integer array costs of length n where costs[i]
# denotes the cost of jumping to index i.
#
# Return the minimum cost to jump to the index n - 1.
#
# Example 1:
#
# Input: nums = [3,2,4,4,1], costs = [3,7,6,4,2]
# Output: 8
# Explanation: You start at index 0.
# - Jump to index 2 with a cost of costs[2] = 6.
# - Jump to index 4 with a cost of costs[4] = 2.
# The total cost is 8. It can be proven that 8 is the minimum cost needed.
# Two other possible paths are from index 0 -> 1 -> 4 and index 0 -> 2 ->
# 3 -> 4.
# These have a total cost of 9 and 12, respectively.
#
# Example 2:
#
# Input: nums = [0,1,2], costs = [1,1,1]
# Output: 2
# Explanation: Start at index 0.
# - Jump to index 1 with a cost of costs[1] = 1.
# - Jump to index 2 with a cost of costs[2] = 1.
# The total cost is 2. Note that you cannot jump directly from index 0 to
# index 2 because nums[0] <= nums[1].
#
# Constraints:
#
# n == nums.length == costs.length
#
# 1 <= n <= 10^5
#
# 0 <= nums[i], costs[i] <= 10^5
#
# @lc code=start
from typing import List
import math


class Solution:
    def minCost(self, nums: List[int], costs: List[int]) -> int:
        """
        Interview explanation:
        From i jump to j>i if (nums[i]<=nums[j] and all between < nums[i]) OR
        (nums[i]>nums[j] and all between >= nums[i]). Cost to land on j is
        costs[j]. Min cost to n-1.

        Algorithm:
        - Monotonic stacks + DP: while popping, update dp[i] from popped indices
          (next greater/equal and next smaller jumps).

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        dp = [math.inf] * n
        dp[0] = 0
        max_st, min_st = [], []
        for i, num in enumerate(nums):
            while max_st and num >= nums[max_st[-1]]:
                dp[i] = min(dp[i], dp[max_st.pop()] + costs[i])
            while min_st and num < nums[min_st[-1]]:
                dp[i] = min(dp[i], dp[min_st.pop()] + costs[i])
            max_st.append(i)
            min_st.append(i)
        return dp[-1]

    def minCost_dp(self, nums: List[int], costs: List[int]) -> int:
        """
        Interview explanation:
        Graph + DP alternate: build next jumps via stacks then relax edges.

        Algorithm:
        - Build adjacency of valid jumps; forward DP min cost.

        Complexity: O(n) time, O(n) space.
        """
        from collections import defaultdict
        n = len(nums)
        g = defaultdict(list)
        stk = []
        for i in range(n - 1, -1, -1):
            while stk and nums[stk[-1]] < nums[i]:
                stk.pop()
            if stk:
                g[i].append(stk[-1])
            stk.append(i)
        stk = []
        for i in range(n - 1, -1, -1):
            while stk and nums[stk[-1]] >= nums[i]:
                stk.pop()
            if stk:
                g[i].append(stk[-1])
            stk.append(i)
        f = [math.inf] * n
        f[0] = 0
        for i in range(n):
            for j in g[i]:
                f[j] = min(f[j], f[i] + costs[j])
        return f[n - 1]
# @lc code=end
