#
# @lc app=leetcode id=1782 lang=python3
#
# [1782] Count Pairs Of Nodes
#
# https://leetcode.com/problems/count-pairs-of-nodes/description/
#
# algorithms
# Hard (43.08%)
# Likes:    352
# Dislikes: 172
# Total Accepted:    10.6K
# Total Submissions: 24.6K
# Testcase Example:  "4"
#
# You are given an undirected graph defined by an integer n, the number of
# nodes, and a 2D integer array edges, the edges in the graph, where edges[i] =
# [u_i, v_i] indicates that there is an undirected edge between u_i and v_i.
# You are also given an integer array queries.
#
# Let incident(a, b) be defined as the number of edges that are connected to
# either node a or b.
#
# The answer to the j^th query is the number of pairs of nodes (a, b) that
# satisfy both of the following conditions:
#
# a < b
#
# incident(a, b) > queries[j]
#
# Return an array answers such that answers.length == queries.length and
# answers[j] is the answer of the j^th query.
#
# Note that there can be multiple edges between the same two nodes.
#
# Example 1:
#
# Input: n = 4, edges = [[1,2],[2,4],[1,3],[2,3],[2,1]], queries = [2,3]
# Output: [6,5]
# Explanation: The calculations for incident(a, b) are shown in the table
# above.
# The answers for each of the queries are as follows:
# - answers[0] = 6. All the pairs have an incident(a, b) value greater than 2.
# - answers[1] = 5. All the pairs except (3, 4) have an incident(a, b) value
# greater than 3.
#
# Example 2:
#
# Input: n = 5, edges = [[1,5],[1,5],[3,4],[2,5],[1,3],[5,1],[2,3],[2,5]],
# queries = [1,2,3,4,5]
# Output: [10,10,9,8,6]
#
# Constraints:
#
# 2 <= n <= 2 * 10^4
#
# 1 <= edges.length <= 10^5
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#
# 1 <= queries.length <= 20
#
# 0 <= queries[j] < edges.length
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def countPairs(self, n: int, edges: List[List[int]], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        Count pairs (a,b) with deg[a]+deg[b] > q, but if edge a-b exists the
        shared incident count uses distinct edges incident to either — so
        formula is deg[a]+deg[b] - shared_edges(a,b) > q. Classic: sort degrees
        + two pointers for deg[a]+deg[b]>q, then subtract false positives where
        edge multiplicity makes the true value ≤ q.

        Algorithm:
        - deg[], edge multiplicity map.
        - sorted deg; for each query two-pointer count pairs with deg sum > q.
        - For each edge (u,v): if deg[u]+deg[v]>q but deg[u]+deg[v]-cnt[(u,v)]≤q: −1.

        Complexity: O(n log n + E + Q*(n + E)) typical optimized O((n+E+Q) log n + Q n).
        """
        deg = [0] * (n + 1)
        cnt = Counter()
        for a, b in edges:
            if a > b:
                a, b = b, a
            deg[a] += 1
            deg[b] += 1
            cnt[(a, b)] += 1
        sorted_deg = sorted(deg[1:])
        ans = []
        for q in queries:
            # two pointers on sorted_deg
            res = 0
            l, r = 0, n - 1
            while l < r:
                if sorted_deg[l] + sorted_deg[r] > q:
                    res += r - l
                    r -= 1
                else:
                    l += 1
            for (a, b), c in cnt.items():
                if deg[a] + deg[b] > q and deg[a] + deg[b] - c <= q:
                    res -= 1
            ans.append(res)
        return ans
# @lc code=end
