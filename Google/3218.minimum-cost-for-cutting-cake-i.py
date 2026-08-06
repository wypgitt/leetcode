#
# @lc app=leetcode id=3218 lang=python3
#
# [3218] Minimum Cost for Cutting Cake I
#
# https://leetcode.com/problems/minimum-cost-for-cutting-cake-i/description/
#
# algorithms
# Medium (58.16%)
# Likes:    205
# Dislikes: 8
# Total Accepted:    31.8K
# Total Submissions: 54.7K
# Testcase Example:  "3\n2\n[1,3]\n[5]"
#
#
# There is an m x n cake that needs to be cut into 1 x 1 pieces.
#
# You are given integers m, n, and two arrays:
#
# horizontalCut of size m - 1, where horizontalCut[i] represents the cost
# to cut along the horizontal line i.
#
# verticalCut of size n - 1, where verticalCut[j] represents the cost to
# cut along the vertical line j.
#
# In one operation, you can choose any piece of cake that is not yet a 1 x
# 1 square and perform one of the following cuts:
#
# Cut along a horizontal line i at a cost of horizontalCut[i].
#
# Cut along a vertical line j at a cost of verticalCut[j].
#
# After the cut, the piece of cake is divided into two distinct pieces.
#
# The cost of a cut depends only on the initial cost of the line and does
# not change.
#
# Return the minimum total cost to cut the entire cake into 1 x 1 pieces.
#
# Example 1:
#
# Input: m = 3, n = 2, horizontalCut = [1,3], verticalCut = [5]
#
# Output: 13
#
# Explanation:
#
# Perform a cut on the vertical line 0 with cost 5, current total cost is
# 5.
#
# Perform a cut on the horizontal line 0 on 3 x 1 subgrid with cost 1.
#
# Perform a cut on the horizontal line 0 on 3 x 1 subgrid with cost 1.
#
# Perform a cut on the horizontal line 1 on 2 x 1 subgrid with cost 3.
#
# Perform a cut on the horizontal line 1 on 2 x 1 subgrid with cost 3.
#
# The total cost is 5 + 1 + 1 + 3 + 3 = 13.
#
# Example 2:
#
# Input: m = 2, n = 2, horizontalCut = [7], verticalCut = [4]
#
# Output: 15
#
# Explanation:
#
# Perform a cut on the horizontal line 0 with cost 7.
#
# Perform a cut on the vertical line 0 on 1 x 2 subgrid with cost 4.
#
# Perform a cut on the vertical line 0 on 1 x 2 subgrid with cost 4.
#
# The total cost is 7 + 4 + 4 = 15.
#
# Constraints:
#
# 1 <= m, n <= 20
#
# horizontalCut.length == m - 1
#
# verticalCut.length == n - 1
#
# 1 <= horizontalCut[i], verticalCut[i] <= 10^3
#

# @lc code=start
from typing import List


class Solution:
    def minimumCost(self, m: int, n: int, horizontalCut: List[int], verticalCut: List[int]) -> int:
        """
        Interview explanation:
        Cutting a cake into 1x1 pieces: each cut cost is multiplied by how many
        pieces it crosses. Greedy: always make the currently most expensive
        remaining cut first (same as classic chocolate-breaking).

        Algorithm:
        - Sort both cut arrays descending.
        - Track horizontal/vertical piece counts (start at 1).
        - Repeatedly take the larger next cut; add cost * opposite piece count;
          increment the matching piece count.

        Complexity: O((m+n) log (m+n)) time, O(1) extra space besides sort.
        """
        horizontalCut = sorted(horizontalCut, reverse=True)
        verticalCut = sorted(verticalCut, reverse=True)
        h_pieces = v_pieces = 1
        i = j = 0
        ans = 0
        while i < len(horizontalCut) and j < len(verticalCut):
            if horizontalCut[i] >= verticalCut[j]:
                ans += horizontalCut[i] * v_pieces
                h_pieces += 1
                i += 1
            else:
                ans += verticalCut[j] * h_pieces
                v_pieces += 1
                j += 1
        while i < len(horizontalCut):
            ans += horizontalCut[i] * v_pieces
            i += 1
        while j < len(verticalCut):
            ans += verticalCut[j] * h_pieces
            j += 1
        return ans
# @lc code=end
