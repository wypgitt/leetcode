#
# @lc app=leetcode id=1981 lang=python3
#
# [1981] Minimize the Difference Between Target and Chosen Elements
#
# https://leetcode.com/problems/minimize-the-difference-between-target-and-chosen-elements/description/
#
# algorithms
# Medium (37.14%)
# Likes:    1074
# Dislikes: 146
# Total Accepted:    40.8K
# Total Submissions: 110K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# You are given an m x n integer matrix mat and an integer target.
#
# Choose one integer from each row in the matrix such that the absolute
# difference between target and the sum of the chosen elements is minimized.
#
# Return the minimum absolute difference.
#
# The absolute difference between two numbers a and b is the absolute value of
# a - b.
#
# Example 1:
#
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]], target = 13
# Output: 0
# Explanation: One possible choice is to:
# - Choose 1 from the first row.
# - Choose 5 from the second row.
# - Choose 7 from the third row.
# The sum of the chosen elements is 13, which equals the target, so the
# absolute difference is 0.
#
# Example 2:
#
# Input: mat = [[1],[2],[3]], target = 100
# Output: 94
# Explanation: The best possible choice is to:
# - Choose 1 from the first row.
# - Choose 2 from the second row.
# - Choose 3 from the third row.
# The sum of the chosen elements is 6, and the absolute difference is 94.
#
# Example 3:
#
# Input: mat = [[1,2,9,8,7]], target = 6
# Output: 1
# Explanation: The best choice is to choose 7 from the first row.
# The absolute difference is 1.
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 70
#
# 1 <= mat[i][j] <= 70
#
# 1 <= target <= 800
#

# @lc code=start
from typing import List


class Solution:
    def minimizeTheDifference(self, mat: List[List[int]], target: int) -> int:
        """
        Interview explanation:
        Pick one element per row; minimize |sum - target|. DP set of achievable
        sums (prune above target + best).

        Algorithm:
        - Start {0}; for each row, new sums = {s+x for s in cur for x in row}.
        - Optionally cap sums > target by tracking only needed range.

        Complexity: O(rows * cols * S) where S is sum bound; O(S) space.
        """
        possible = {0}
        for row in mat:
            uniq = set(row)
            nxt = set()
            for s in possible:
                for x in uniq:
                    nxt.add(s + x)
            possible = nxt
        return min(abs(s - target) for s in possible)

    def minimizeTheDifference_pruned(self, mat: List[List[int]], target: int) -> int:
        """
        Interview explanation:
        Alternate DP with pruning: drop sums that already exceed target by more
        than current best answer.

        Algorithm:
        - Maintain set; after each row update best = min |s-target|; prune large.

        Complexity: typically much smaller than full sum-set DP.
        """
        possible = {0}
        for row in mat:
            uniq = sorted(set(row))
            nxt = set()
            for s in possible:
                for x in uniq:
                    nxt.add(s + x)
            # prune: keep all <= target and the smallest > target
            below = {s for s in nxt if s <= target}
            above = [s for s in nxt if s > target]
            possible = below
            if above:
                possible.add(min(above))
        return min(abs(s - target) for s in possible)
# @lc code=end

