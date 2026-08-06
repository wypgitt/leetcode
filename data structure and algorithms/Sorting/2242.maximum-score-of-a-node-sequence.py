#
# @lc app=leetcode id=2242 lang=python3
#
# [2242] Maximum Score of a Node Sequence
#
# https://leetcode.com/problems/maximum-score-of-a-node-sequence/description/
#
# algorithms
# Hard (40.36%)
# Likes:    591
# Dislikes: 21
# Total Accepted:    18.4K
# Total Submissions: 45.6K
# Testcase Example:  "[5,2,9,8,4]\n[[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]"
#
# There is an undirected graph with n nodes, numbered from 0 to n - 1.
#
# You are given a 0-indexed integer array scores of length n where scores[i]
# denotes the score of node i. You are also given a 2D integer array edges where
# edges[i] = [a_i, b_i] denotes that there exists an undirected edge connecting
# nodes a_i and b_i.
#
# A node sequence is valid if it meets the following conditions:
#
#
# There is an edge connecting every pair of adjacent nodes in the sequence.
#
#
# No node appears more than once in the sequence.
#
# The score of a node sequence is defined as the sum of the scores of the nodes
# in the sequence.
#
# Return the maximum score of a valid node sequence with a length of 4. If no
# such sequence exists, return -1.
#
#
#
# Example 1:
#
# Input: scores = [5,2,9,8,4], edges = [[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]
# Output: 24
# Explanation: The figure above shows the graph and the chosen node sequence
# [0,1,2,3].
# The score of the node sequence is 5 + 2 + 9 + 8 = 24.
# It can be shown that no other node sequence has a score of more than 24.
# Note that the sequences [3,1,2,0] and [1,0,2,3] are also valid and have a
# score of 24.
# The sequence [0,3,2,4] is not valid since no edge connects nodes 0 and 3.
#
# Example 2:
#
# Input: scores = [9,20,6,4,11,12], edges = [[0,3],[5,3],[2,4],[1,3]]
# Output: -1
# Explanation: The figure above shows the graph.
# There are no valid node sequences of length 4, so we return -1.
#
#
#
# Constraints:
#
#
# n == scores.length
#
#
# 4 <= n <= 5 * 10^4
#
#
# 1 <= scores[i] <= 10^8
#
#
# 0 <= edges.length <= 5 * 10^4
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i <= n - 1
#
#
# a_i != b_i
#
#
# There are no duplicate edges.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def maximumScore(self, scores: List[int], edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Undirected graph; find a path of 4 distinct nodes a-b-c-d maximizing
        scores[a]+scores[b]+scores[c]+scores[d], or -1.

        Algorithm:
        - For each node keep top-3 neighbors by score. For each edge (b,c), try
          best neighbors a of b and d of c distinct from each other and b,c.

        Complexity: O(n + m log 3) ~ O(n+m) time, O(n) space.
        """
        n = len(scores)
        top = [[] for _ in range(n)]  # min-heaps of (score, node) size <=3

        def add(u: int, v: int) -> None:
            heapq.heappush(top[u], (scores[v], v))
            if len(top[u]) > 3:
                heapq.heappop(top[u])

        for u, v in edges:
            add(u, v)
            add(v, u)

        # convert to sorted lists descending
        neigh = [sorted(h, reverse=True) for h in top]
        ans = -1
        for b, c in edges:
            for sb, a in neigh[b]:
                if a == c:
                    continue
                for sc, d in neigh[c]:
                    if d == b or d == a:
                        continue
                    ans = max(ans, scores[a] + scores[b] + scores[c] + scores[d])
        return ans
# @lc code=end
