#
# @lc app=leetcode id=2201 lang=python3
#
# [2201] Count Artifacts That Can Be Extracted
#
# https://leetcode.com/problems/count-artifacts-that-can-be-extracted/description/
#
# algorithms
# Medium (57.36%)
# Likes:    228
# Dislikes: 205
# Total Accepted:    23.9K
# Total Submissions: 41.7K
# Testcase Example:  "2\n[[0,0,0,0],[0,1,1,1]]\n[[0,0],[0,1]]"
#
# There is an n x n 0-indexed grid with some artifacts buried in it. You are
# given the integer n and a 0-indexed 2D integer array artifacts describing the
# positions of the rectangular artifacts where artifacts[i] = [r1_i, c1_i, r2_i,
# c2_i] denotes that the i^th artifact is buried in the subgrid where:
#
#
# (r1_i, c1_i) is the coordinate of the top-left cell of the i^th artifact and
#
#
# (r2_i, c2_i) is the coordinate of the bottom-right cell of the i^th artifact.
#
# You will excavate some cells of the grid and remove all the mud from them. If
# the cell has a part of an artifact buried underneath, it will be uncovered. If
# all the parts of an artifact are uncovered, you can extract it.
#
# Given a 0-indexed 2D integer array dig where dig[i] = [r_i, c_i] indicates
# that you will excavate the cell (r_i, c_i), return the number of artifacts
# that you can extract.
#
# The test cases are generated such that:
#
#
# No two artifacts overlap.
#
#
# Each artifact only covers at most 4 cells.
#
#
# The entries of dig are unique.
#
#
#
# Example 1:
#
# Input: n = 2, artifacts = [[0,0,0,0],[0,1,1,1]], dig = [[0,0],[0,1]]
# Output: 1
# Explanation:
# The different colors represent different artifacts. Excavated cells are
# labeled with a 'D' in the grid.
# There is 1 artifact that can be extracted, namely the red artifact.
# The blue artifact has one part in cell (1,1) which remains uncovered, so we
# cannot extract it.
# Thus, we return 1.
#
# Example 2:
#
# Input: n = 2, artifacts = [[0,0,0,0],[0,1,1,1]], dig = [[0,0],[0,1],[1,1]]
# Output: 2
# Explanation: Both the red and blue artifacts have all parts uncovered (labeled
# with a 'D') and can be extracted, so we return 2.
#
#
#
# Constraints:
#
#
# 1 <= n <= 1000
#
#
# 1 <= artifacts.length, dig.length <= min(n^2, 10^5)
#
#
# artifacts[i].length == 4
#
#
# dig[i].length == 2
#
#
# 0 <= r1_i, c1_i, r2_i, c2_i, r_i, c_i <= n - 1
#
#
# r1_i <= r2_i
#
#
# c1_i <= c2_i
#
#
# No two artifacts will overlap.
#
#
# The number of cells covered by an artifact is at most 4.
#
#
# The entries of dig are unique.
#

# @lc code=start
from typing import List


class Solution:
    def digArtifacts(self, n: int, artifacts: List[List[int]], dig: List[List[int]]) -> int:
        """
        Interview explanation:
        Artifacts are axis-aligned rectangles on an n x n grid. Dig uncovers cells;
        an artifact is extractable iff every cell of its rectangle is dug.

        Algorithm:
        - Put dug cells in a set; for each artifact check all cells in [r1..r2]x[c1..c2].

        Complexity: O(n^2 + artifact cells) time, O(|dig|) space.
        """
        dug = {(r, c) for r, c in dig}
        ans = 0
        for r1, c1, r2, c2 in artifacts:
            ok = True
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if (r, c) not in dug:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                ans += 1
        return ans
# @lc code=end
