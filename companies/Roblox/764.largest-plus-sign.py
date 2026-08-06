#
# @lc app=leetcode id=764 lang=python3
#
# [764] Largest Plus Sign
#
# https://leetcode.com/problems/largest-plus-sign/description/
#
# algorithms
# Medium (49.42%)
# Likes:    1547
# Dislikes: 243
# Total Accepted:    71.6K
# Total Submissions: 145K
# Testcase Example:  "5"
#
# You are given an integer n. You have an n x n binary grid grid with all
# values initially 1's except for some indices given in the array mines. The
# i^th element of the array mines is defined as mines[i] = [x_i, y_i] where
# grid[x_i][y_i] == 0.
#
# Return the order of the largest axis-aligned plus sign of 1's contained in
# grid. If there is none, return 0.
#
# An axis-aligned plus sign of 1's of order k has some center grid[r][c] == 1
# along with four arms of length k - 1 going up, down, left, and right, and
# made of 1's. Note that there could be 0's or 1's beyond the arms of the plus
# sign, only the relevant area of the plus sign is checked for 1's.
#
# Example 1:
#
# Input: n = 5, mines = [[4,2]]
# Output: 2
# Explanation: In the above grid, the largest plus sign can only be of order 2.
# One of them is shown.
#
# Example 2:
#
# Input: n = 1, mines = [[0,0]]
# Output: 0
# Explanation: There is no plus sign, so return 0.
#
# Constraints:
#
# 1 <= n <= 500
#
# 1 <= mines.length <= 5000
#
# 0 <= x_i, y_i < n
#
# All the pairs (x_i, y_i) are unique.
#


# @lc code=start
from typing import List, Set, Tuple


class Solution:
    def orderOfLargestPlusSign(self, n: int, mines: List[List[int]]) -> int:
        """
        Interview explanation:
        Order-k plus needs k consecutive 1s in all four directions from center
        (including center). Precompute for each cell the arm length in each
        direction via four linear sweeps; answer is max over cells of min of
        the four arms.

        Algorithm:
        - banned = set of mines; init dp[r][c]=n if not banned else 0
        - For each row: left/right sweeps of consecutive non-mines
        - For each col: up/down sweeps; dp[r][c] = min(dp, arm)
        - Return max dp

        Complexity: O(n^2) time and space.
        """
        banned: Set[Tuple[int, int]] = {(r, c) for r, c in mines}
        dp = [[0] * n for _ in range(n)]
        for r in range(n):
            # left
            arm = 0
            for c in range(n):
                arm = 0 if (r, c) in banned else arm + 1
                dp[r][c] = arm
            # right
            arm = 0
            for c in range(n - 1, -1, -1):
                arm = 0 if (r, c) in banned else arm + 1
                dp[r][c] = min(dp[r][c], arm)
        ans = 0
        for c in range(n):
            arm = 0
            for r in range(n):
                arm = 0 if (r, c) in banned else arm + 1
                dp[r][c] = min(dp[r][c], arm)
            arm = 0
            for r in range(n - 1, -1, -1):
                arm = 0 if (r, c) in banned else arm + 1
                dp[r][c] = min(dp[r][c], arm)
                ans = max(ans, dp[r][c])
        return ans
# @lc code=end

