#
# @lc app=leetcode id=2282 lang=python3
#
# [2282] Number of People That Can Be Seen in a Grid
#
# https://leetcode.com/problems/number-of-people-that-can-be-seen-in-a-grid/description/
#
# algorithms
# Medium (47.38%)
# Likes:    67
# Dislikes: 34
# Total Accepted:    2.7K
# Total Submissions: 5.8K
# Testcase Example:  "[[3,1,4,2,5]]"
#
#
# You are given an m x n 0-indexed 2D array of positive integers heights
# where heights[i][j] is the height of the person standing at position (i,
# j).
#
# A person standing at position (row_1, col_1) can see a person standing
# at position (row_2, col_2) if:
#
# The person at (row_2, col_2) is to the right or below the person at
# (row_1, col_1). More formally, this means that either row_1 == row_2 and
# col_1 < col_2 or row_1 < row_2 and col_1 == col_2.
#
# Everyone in between them is shorter than both of them.
#
# Return an m x n 2D array of integers answer where answer[i][j] is the
# number of people that the person at position (i, j) can see.
#
# Example 1:
#
# Input: heights = [[3,1,4,2,5]]
# Output: [[2,1,2,1,0]]
# Explanation:
# - The person at (0, 0) can see the people at (0, 1) and (0, 2).
#   Note that he cannot see the person at (0, 4) because the person at (0,
# 2) is taller than him.
# - The person at (0, 1) can see the person at (0, 2).
# - The person at (0, 2) can see the people at (0, 3) and (0, 4).
# - The person at (0, 3) can see the person at (0, 4).
# - The person at (0, 4) cannot see anybody.
#
# Example 2:
#
# Input: heights = [[5,1],[3,1],[4,1]]
# Output: [[3,1],[2,1],[1,0]]
# Explanation:
# - The person at (0, 0) can see the people at (0, 1), (1, 0) and (2, 0).
# - The person at (0, 1) can see the person at (1, 1).
# - The person at (1, 0) can see the people at (1, 1) and (2, 0).
# - The person at (1, 1) can see the person at (2, 1).
# - The person at (2, 0) can see the person at (2, 1).
# - The person at (2, 1) cannot see anybody.
#
# Constraints:
#
# 1 <= heights.length <= 400
#
# 1 <= heights[i].length <= 400
#
# 1 <= heights[i][j] <= 10^5
#
# @lc code=start
from typing import List


class Solution:
    def seePeople(self, heights: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Person (r1,c1) sees (r2,c2) to the right or below if everyone between is
        shorter than both. Count visible people per cell.

        Algorithm:
        - Monotonic stack per row (rightward) and per column (downward), like
          "visible people in a queue"; sum both directions.

        Complexity: O(m*n) time, O(max(m,n)) extra space.
        """
        def f(nums: List[int]) -> List[int]:
            n = len(nums)
            stk = []
            ans = [0] * n
            for i in range(n - 1, -1, -1):
                while stk and stk[-1] < nums[i]:
                    ans[i] += 1
                    stk.pop()
                if stk:
                    ans[i] += 1
                while stk and stk[-1] == nums[i]:
                    stk.pop()
                stk.append(nums[i])
            return ans

        ans = [f(row) for row in heights]
        m, n = len(heights), len(heights[0])
        for j in range(n):
            add = f([heights[i][j] for i in range(m)])
            for i in range(m):
                ans[i][j] += add[i]
        return ans
# @lc code=end
