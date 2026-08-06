#
# @lc app=leetcode id=3858 lang=python3
#
# [3858] Minimum Bitwise OR From Grid
#
# https://leetcode.com/problems/minimum-bitwise-or-from-grid/description/
#
# algorithms
# Medium (27.53%)
# Likes:    139
# Dislikes: 3
# Total Accepted:    14.8K
# Total Submissions: 53.6K
# Testcase Example:  "[[1,5],[2,4]]"
#
#
# You are given a 2D integer array grid of size m x n.
#
# You must select exactly one integer from each row of the grid.
#
# Return an integer denoting the minimum possible bitwise OR of the
# selected integers from each row.
#
# Example 1:
#
# Input: grid = [[1,5],[2,4]]
#
# Output: 3
#
# Explanation:
#
# Choose 1 from the first row and 2 from the second row.
#
# The bitwise OR of 1 | 2 = 3​​​​​​​, which is the minimum possible.
#
# Example 2:
#
# Input: grid = [[3,5],[6,4]]
#
# Output: 5
#
# Explanation:
#
# Choose 5 from the first row and 4 from the second row.
#
# The bitwise OR of 5 | 4 = 5​​​​​​​, which is the minimum possible.
#
# Example 3:
#
# Input: grid = [[7,9,8]]
#
# Output: 7
#
# Explanation:
#
# Choosing 7 gives the minimum bitwise OR.
#
# Constraints:
#
# 1 <= m == grid.length <= 10^5
#
# 1 <= n == grid[i].length <= 10^5
#
# m * n <= 10^5
#
# 1 <= grid[i][j] <= 10^5​​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def minimumOR(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Pick one value per row minimizing the OR. Greedily decide bits MSB→LSB:
        keep a bit off if every row still has a value compatible with bits already
        forced on and lower bits free.

        Algorithm:
        - ans accumulates forced-on bits.
        - For bit i: mask = ans | ((1<<i)-1). If some row has no x with
          (x|mask)==mask, bit i must be set in ans.

        Complexity: O(B * total cells) time with B≤17 here, O(1) space.
        """
        mx = max(max(row) for row in grid)
        ans = 0
        for i in range(mx.bit_length() - 1, -1, -1):
            mask = ans | ((1 << i) - 1)
            if any(all((x | mask) != mask for x in row) for row in grid):
                ans |= 1 << i
        return ans
# @lc code=end
