#
# @lc app=leetcode id=265 lang=python3
#
# [265] Paint House II
#
# https://leetcode.com/problems/paint-house-ii/description/
#
# algorithms
# Hard (57.24%)
# Likes:    1352
# Dislikes: 40
# Total Accepted:    146.2K
# Total Submissions: 255.3K
# Testcase Example:  "[[1,5,3],[2,9,4]]"
#
#
# There are a row of n houses, each house can be painted with one of the k
# colors. The cost of painting each house with a certain color is
# different. You have to paint all the houses such that no two adjacent
# houses have the same color.
#
# The cost of painting each house with a certain color is represented by
# an n x k cost matrix costs.
#
# For example, costs[0][0] is the cost of painting house 0 with color 0;
# costs[1][2] is the cost of painting house 1 with color 2, and so on...
#
# Return the minimum cost to paint all houses.
#
# Example 1:
#
# Input: costs = [[1,5,3],[2,9,4]]
# Output: 5
# Explanation:
# Paint house 0 into color 0, paint house 1 into color 2. Minimum cost: 1
# + 4 = 5;
# Or paint house 0 into color 2, paint house 1 into color 0. Minimum cost:
# 3 + 2 = 5.
#
# Example 2:
#
# Input: costs = [[1,3],[2,4]]
# Output: 5
#
# Constraints:
#
# costs.length == n
#
# costs[i].length == k
#
# 1 <= n <= 100
#
# 2 <= k <= 20
#
# 1 <= costs[i][j] <= 20
#
# Follow up: Could you solve it in O(nk) runtime?
#
# @lc code=start
from typing import List


class Solution:
    def minCostII(self, costs: List[List[int]]) -> int:
        """
        Interview explanation:
        Paint n houses with k colors; adjacent houses differ. Track previous
        row's min and second-min costs so each house is O(k): use min unless
        same color, then second min.

        Algorithm:
        - Keep prev_min, prev_second, prev_min_color.
        - For each house/color: cost += prev_min (or prev_second if same color).
        - Update running min/second for the next house.

        Complexity: O(nk) time, O(1) extra space.
        """
        if not costs:
            return 0
        n, k = len(costs), len(costs[0])
        prev_min = prev_second = 0
        prev_color = -1

        for i in range(n):
            cur_min = cur_second = float("inf")
            cur_color = -1
            for c in range(k):
                val = costs[i][c] + (prev_second if c == prev_color else prev_min)
                if val < cur_min:
                    cur_second = cur_min
                    cur_min = val
                    cur_color = c
                elif val < cur_second:
                    cur_second = val
            prev_min, prev_second, prev_color = cur_min, cur_second, cur_color

        return int(prev_min)
# @lc code=end
