#
# @lc app=leetcode id=3888 lang=python3
#
# [3888] Minimum Operations to Make All Grid Elements Equal
#
# https://leetcode.com/problems/minimum-operations-to-make-all-grid-elements-equal/description/
#
# algorithms
# Hard (62.57%)
# Likes:    1
# Dislikes: 1
# Total Accepted:    336
# Total Submissions: 537
# Testcase Example:  "[[3,3,5],[3,3,5]]\n2"
#
#
# You are given a 2D integer array grid of size m × n, and an integer k.
#
# In one operation, you can:
#
# Select any k x k submatrix of grid, and
#
# Increment all elements inside that submatrix by 1.
#
# Return the minimum number of operations required to make all elements in
# the grid equal. If it is not possible, return -1.
#
# A submatrix (x1, y1, x2, y2) is a matrix that forms by choosing all
# cells matrix[x][y] where x1 <= x <= x2 and y1 <= y <= y2.
#
# Example 1:
#
# Input: grid = [[3,3,5],[3,3,5]], k = 2
#
# Output: 2
#
# Explanation:
#
# Choose the left 2 x 2 submatrix (covering the first two columns) and
# apply the operation twice.
#
# After 1 operation: [[4, 4, 5], [4, 4, 5]]
#
# After 2 operations: [[5, 5, 5], [5, 5, 5]]
#
# All elements become equal to 5. Thus, the minimum number of operations
# is 2.
#
# Example 2:
#
# Input: grid = [[1,2],[2,3]], k = 1
#
# Output: 4
#
# Explanation:
#
# Since k = 1, each operation increments a single cell grid[i][j] by 1. To
# make all elements equal, the final value must be 3.
#
# Increase grid[0][0] = 1 to 3, requiring 2 operations.
#
# Increase grid[0][1] = 2 to 3, requiring 1 operation.
#
# Increase grid[1][0] = 2 to 3, requiring 1 operation.
#
# Thus, the minimum number of operations is 2 + 1 + 1 + 0 = 4.
#
# Constraints:
#
# 1 <= m == grid.length <= 1000
#
# 1 <= n == grid[i].length <= 1000
#
# -10^5 <= grid[i][j] <= 10^5
#
# 1 <= k <= min(m, n)
#

# @lc code=start
class Solution:
    def minOperations(self, grid: list[list[int]], k: int) -> int:
        """
        Interview explanation:
        Only increments are allowed, so the target T ≥ max(grid). Greedily place
        k×k ops from top-left; 2D difference tracks pending increments.

        Algorithm:
        - For T in {max, max+1}: scan cells; if below T and a k×k fits, apply
          needed ops via difference array; if overshoot or no room, fail.
        - Return the first feasible T's op count, else -1.

        Complexity: O(m n) time, O(m n) space.
        """
        m, n = len(grid), len(grid[0])
        mx = max(max(row) for row in grid)

        def check(target: int) -> int:
            diff = [[0] * (n + 2) for _ in range(m + 2)]
            total = 0
            for i, row in enumerate(grid, 1):
                for j, val in enumerate(row, 1):
                    diff[i][j] += diff[i - 1][j] + diff[i][j - 1] - diff[i - 1][j - 1]
                    cur = val + diff[i][j]
                    if cur > target:
                        return -1
                    if cur < target:
                        if i + k - 1 > m or j + k - 1 > n:
                            return -1
                        need = target - cur
                        total += need
                        diff[i][j] += need
                        diff[i + k][j] -= need
                        diff[i][j + k] -= need
                        diff[i + k][j + k] += need
            return total

        for t in (mx, mx + 1):
            res = check(t)
            if res != -1:
                return res
        return -1
# @lc code=end
