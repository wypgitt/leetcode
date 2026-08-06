#
# @lc app=leetcode id=3067 lang=python3
#
# [3067] Count Pairs of Connectable Servers in a Weighted Tree Network
#
# https://leetcode.com/problems/count-pairs-of-connectable-servers-in-a-weighted-tree-network/description/
#
# algorithms
# Medium (56.39%)
# Likes:    245
# Dislikes: 29
# Total Accepted:    17.3K
# Total Submissions: 30.7K
# Testcase Example:  "[[0,1,1],[1,2,5],[2,3,13],[3,4,9],[4,5,2]]\n1"
#
#
# You are given an unrooted weighted tree with n vertices representing
# servers numbered from 0 to n - 1, an array edges where edges[i] = [a_i,
# b_i, weight_i] represents a bidirectional edge between vertices a_i and
# b_i of weight weight_i. You are also given an integer signalSpeed.
#
# Two servers a and b are connectable through a server c if:
#
# a < b, a != c and b != c.
#
# The distance from c to a is divisible by signalSpeed.
#
# The distance from c to b is divisible by signalSpeed.
#
# The path from c to b and the path from c to a do not share any edges.
#
# Return an integer array count of length n where count[i] is the number
# of server pairs that are connectable through the server i.
#
# Example 1:
#
# Input: edges = [[0,1,1],[1,2,5],[2,3,13],[3,4,9],[4,5,2]], signalSpeed =
# 1
# Output: [0,4,6,6,4,0]
# Explanation: Since signalSpeed is 1, count[c] is equal to the number of
# pairs of paths that start at c and do not share any edges.
# In the case of the given path graph, count[c] is equal to the number of
# servers to the left of c multiplied by the servers to the right of c.
#
# Example 2:
#
# Input: edges = [[0,6,3],[6,5,3],[0,3,1],[3,2,7],[3,1,6],[3,4,2]],
# signalSpeed = 3
# Output: [2,0,0,0,0,0,2]
# Explanation: Through server 0, there are 2 pairs of connectable servers:
# (4, 5) and (4, 6).
# Through server 6, there are 2 pairs of connectable servers: (4, 5) and
# (0, 5).
# It can be shown that no two servers are connectable through servers
# other than 0 and 6.
#
# Constraints:
#
# 2 <= n <= 1000
#
# edges.length == n - 1
#
# edges[i].length == 3
#
# 0 <= a_i, b_i < n
#
# edges[i] = [a_i, b_i, weight_i]
#
# 1 <= weight_i <= 10^6
#
# 1 <= signalSpeed <= 10^6
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def countPairsOfConnectableServers(self, edges: List[List[int]], signalSpeed: int) -> List[int]:
        """
        Interview explanation:
        For each server c as hub, count pairs (a,b) in different edge-disjoint
        branches from c whose distances to c are multiples of signalSpeed.

        Algorithm:
        - Build adjacency list. For each c, DFS each neighbor-subtree separately,
          counting nodes with dist % signalSpeed == 0. Pair counts across branches:
          for branch counts c_i, add c_i * (sum of prior branch counts).

        Complexity: O(n^2) time, O(n) space (n <= 1000).
        """
        n = len(edges) + 1
        g: List[List[tuple]] = [[] for _ in range(n)]
        for a, b, w in edges:
            g[a].append((b, w))
            g[b].append((a, w))

        def dfs(u: int, parent: int, dist: int) -> int:
            cnt = 1 if dist % signalSpeed == 0 else 0
            for v, w in g[u]:
                if v != parent:
                    cnt += dfs(v, u, dist + w)
            return cnt

        ans = [0] * n
        for c in range(n):
            total = 0
            pairs = 0
            for v, w in g[c]:
                cnt = dfs(v, c, w)
                pairs += total * cnt
                total += cnt
            ans[c] = pairs
        return ans
# @lc code=end
