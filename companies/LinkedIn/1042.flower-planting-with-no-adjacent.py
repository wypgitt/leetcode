#
# @lc app=leetcode id=1042 lang=python3
#
# [1042] Flower Planting With No Adjacent
#
# https://leetcode.com/problems/flower-planting-with-no-adjacent/description/
#
# algorithms
# Medium (54.02%)
# Likes:    1590
# Dislikes: 727
# Total Accepted:    108K
# Total Submissions: 200K
# Testcase Example:  "3"
#
# You have n gardens, labeled from 1 to n, and an array paths where paths[i] =
# [x_i, y_i] describes a bidirectional path between garden x_i to garden y_i.
# In each garden, you want to plant one of 4 types of flowers.
#
# All gardens have at most 3 paths coming into or leaving it.
#
# Your task is to choose a flower type for each garden such that, for any two
# gardens connected by a path, they have different types of flowers.
#
# Return any such a choice as an array answer, where answer[i] is the type of
# flower planted in the (i+1)^th garden. The flower types are denoted 1, 2, 3,
# or 4. It is guaranteed an answer exists.
#
# Example 1:
#
# Input: n = 3, paths = [[1,2],[2,3],[3,1]]
# Output: [1,2,3]
# Explanation:
# Gardens 1 and 2 have different types.
# Gardens 2 and 3 have different types.
# Gardens 3 and 1 have different types.
# Hence, [1,2,3] is a valid answer. Other valid answers include [1,2,4],
# [1,4,2], and [3,2,1].
#
# Example 2:
#
# Input: n = 4, paths = [[1,2],[3,4]]
# Output: [1,2,1,2]
#
# Example 3:
#
# Input: n = 4, paths = [[1,2],[2,3],[3,4],[4,1],[1,3],[2,4]]
# Output: [1,2,3,4]
#
# Constraints:
#
# 1 <= n <= 10^4
#
# 0 <= paths.length <= 2 * 10^4
#
# paths[i].length == 2
#
# 1 <= x_i, y_i <= n
#
# x_i != y_i
#
# Every garden has at most 3 paths coming into or leaving it.
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def gardenNoAdj(self, n: int, paths: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Graph is 3-regular max degree ≤3 with 4 colors available, so greedy
        coloring always works: for each garden pick a color unused by neighbors.

        Algorithm:
        - Build adj; ans[i]=0
        - For garden 1..n: used = colors of neighbors; pick smallest in 1..4 free

        Complexity: O(n + e) time, O(n + e) space.
        """
        adj = defaultdict(list)
        for a, b in paths:
            adj[a].append(b)
            adj[b].append(a)
        ans = [0] * (n + 1)
        for g in range(1, n + 1):
            used = {ans[nei] for nei in adj[g]}
            for c in range(1, 5):
                if c not in used:
                    ans[g] = c
                    break
        return ans[1:]
# @lc code=end
