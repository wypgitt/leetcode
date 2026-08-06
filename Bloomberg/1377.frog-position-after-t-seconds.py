#
# @lc app=leetcode id=1377 lang=python3
#
# [1377] Frog Position After T Seconds
#
# https://leetcode.com/problems/frog-position-after-t-seconds/description/
#
# algorithms
# Hard (38.71%)
# Likes:    853
# Dislikes: 151
# Total Accepted:    45.2K
# Total Submissions: 117K
# Testcase Example:  "7"
#
# Given an undirected tree consisting of n vertices numbered from 1 to n. A
# frog starts jumping from vertex 1. In one second, the frog jumps from its
# current vertex to another unvisited vertex if they are directly connected.
# The frog can not jump back to a visited vertex. In case the frog can jump to
# several vertices, it jumps randomly to one of them with the same probability.
# Otherwise, when the frog can not jump to any unvisited vertex, it jumps
# forever on the same vertex.
#
# The edges of the undirected tree are given in the array edges, where edges[i]
# = [a_i, b_i] means that exists an edge connecting the vertices a_i and b_i.
#
# Return the probability that after t seconds the frog is on the vertex target.
# Answers within 10^-5 of the actual answer will be accepted.
#
# Example 1:
#
# Input: n = 7, edges = [[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]], t = 2, target =
# 4
# Output: 0.16666666666666666
# Explanation: The figure above shows the given graph. The frog starts at
# vertex 1, jumping with 1/3 probability to the vertex 2 after second 1 and
# then jumping with 1/2 probability to vertex 4 after second 2. Thus the
# probability for the frog is on the vertex 4 after 2 seconds is 1/3 * 1/2 =
# 1/6 = 0.16666666666666666.
#
# Example 2:
#
# Input: n = 7, edges = [[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]], t = 1, target =
# 7
# Output: 0.3333333333333333
# Explanation: The figure above shows the given graph. The frog starts at
# vertex 1, jumping with 1/3 = 0.3333333333333333 probability to the vertex 7
# after second 1.
#
# Constraints:
#
# 1 <= n <= 100
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 1 <= a_i, b_i <= n
#
# 1 <= t <= 50
#
# 1 <= target <= n
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def frogPosition(self, n: int, edges: List[List[int]], t: int, target: int) -> float:
        """
        Interview explanation:
        Tree frog starts at 1; each second jumps to a random unused neighbor,
        or stays forever at a leaf. Return probability of being at target at time t.

        Algorithm:
        - DFS(u, parent, time_left, prob): if time_left==0 or no children:
          return prob if u==target else 0
          (if u==target mid-way with children left, return 0)
        - Branch equally among non-parent neighbors

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)

        def dfs(u: int, parent: int, time: int, prob: float) -> float:
            children = [v for v in g[u] if v != parent]
            if time == 0 or not children:
                return prob if u == target else 0.0
            if u == target:
                return 0.0
            share = prob / len(children)
            for v in children:
                ans = dfs(v, u, time - 1, share)
                if ans > 0:
                    return ans
            return 0.0

        return dfs(1, -1, t, 1.0)
# @lc code=end
