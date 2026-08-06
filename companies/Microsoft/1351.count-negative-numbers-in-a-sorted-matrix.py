#
# @lc app=leetcode id=1351 lang=python3
#
# [1351] Count Negative Numbers in a Sorted Matrix
#
# https://leetcode.com/problems/count-negative-numbers-in-a-sorted-matrix/description/
#
# algorithms
# Easy (79.71%)
# Likes:    5527
# Dislikes: 147
# Total Accepted:    689K
# Total Submissions: 864K
# Testcase Example:  "[[4,3,2,-1],[3,2,1,-1],[1,1,-1,-2],[-1,-1,-2,-3]]"
#
# Given a m x n matrix grid which is sorted in non-increasing order both
# row-wise and column-wise, return the number of negative numbers in grid.
#
# Example 1:
#
# Input: grid = [[4,3,2,-1],[3,2,1,-1],[1,1,-1,-2],[-1,-1,-2,-3]]
# Output: 8
# Explanation: There are 8 negatives number in the matrix.
#
# Example 2:
#
# Input: grid = [[3,2],[1,0]]
# Output: 0
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 100
#
# -100 <= grid[i][j] <= 100
#
# Follow up: Could you find an O(n + m) solution?
#

# @lc code=start

from typing import List


class Solution:
    def countNegatives(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Matrix is sorted non-increasing in rows and columns. Start at top-right:
        if negative, entire suffix of the column below is negative; else move left.

        Algorithm:
        - r,c = 0,n-1; while in bounds: if grid[r][c]<0: ans+=m-r; c-=1 else r+=1

        Complexity: O(m+n) time, O(1) space.
        """
        m, n = len(grid), len(grid[0])
        r, c = 0, n - 1
        ans = 0
        while r < m and c >= 0:
            if grid[r][c] < 0:
                ans += m - r
                c -= 1
            else:
                r += 1
        return ans

    def countNegatives_binary(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: binary search first negative index in each non-increasing row.

        Algorithm:
        - For each row, bisect leftmost index with value < 0; add n-idx.

        Complexity: O(m log n) time, O(1) space.
        """
        ans = 0
        for row in grid:
            lo, hi = 0, len(row)
            while lo < hi:
                mid = (lo + hi) // 2
                if row[mid] < 0:
                    hi = mid
                else:
                    lo = mid + 1
            ans += len(row) - lo
        return ans
# @lc code=end
