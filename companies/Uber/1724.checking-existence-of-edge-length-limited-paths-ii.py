#
# @lc app=leetcode id=1724 lang=python3
#
# [1724] Checking Existence of Edge Length Limited Paths II
#
# https://leetcode.com/problems/checking-existence-of-edge-length-limited-paths-ii/description/
#
# algorithms
# Hard (51.72%)
# Likes:    125
# Dislikes: 10
# Total Accepted:    4.3K
# Total Submissions: 8.4K
# Testcase Example:  "[\"DistanceLimitedPathsExist\",\"query\",\"query\",\"query\",\"query\"]\n[[6,[[0,2,4],[0,3,2],[1,2,3],[2,3,1],[4,5,5]]],[2,3,2],[1,3,3],[2,0,3],[0,5,6]]"
#
#
# An undirected graph of n nodes is defined by edgeList, where edgeList[i]
# = [u_i, v_i, dis_i] denotes an edge between nodes u_i and v_i with
# distance dis_i. Note that there may be multiple edges between two nodes,
# and the graph may not be connected.
#
# Implement the DistanceLimitedPathsExist class:
#
# DistanceLimitedPathsExist(int n, int[][] edgeList) Initializes the class
# with an undirected graph.
#
# boolean query(int p, int q, int limit) Returns true if there exists a
# path from p to q such that each edge on the path has a distance strictly
# less than limit, and otherwise false.
#
# Example 1:
#
# Input
# ["DistanceLimitedPathsExist", "query", "query", "query", "query"]
# [[6, [[0, 2, 4], [0, 3, 2], [1, 2, 3], [2, 3, 1], [4, 5, 5]]], [2, 3,
# 2], [1, 3, 3], [2, 0, 3], [0, 5, 6]]
# Output
# [null, true, false, true, false]
#
# Explanation
# DistanceLimitedPathsExist distanceLimitedPathsExist = new
# DistanceLimitedPathsExist(6, [[0, 2, 4], [0, 3, 2], [1, 2, 3], [2, 3,
# 1], [4, 5, 5]]);
# distanceLimitedPathsExist.query(2, 3, 2); // return true. There is an
# edge from 2 to 3 of distance 1, which is less than 2.
# distanceLimitedPathsExist.query(1, 3, 3); // return false. There is no
# way to go from 1 to 3 with distances strictly less than 3.
# distanceLimitedPathsExist.query(2, 0, 3); // return true. There is a way
# to go from 2 to 0 with distance < 3: travel from 2 to 3 to 0.
# distanceLimitedPathsExist.query(0, 5, 6); // return false. There are no
# paths from 0 to 5.
#
# Constraints:
#
# 2 <= n <= 10^4
#
# 0 <= edgeList.length <= 10^4
#
# edgeList[i].length == 3
#
# 0 <= u_i, v_i, p, q <= n-1
#
# u_i != v_i
#
# p != q
#
# 1 <= dis_i, limit <= 10^9
#
# At most 10^4 calls will be made to query.
#
# @lc code=start
from typing import List


class DistanceLimitedPathsExist:
    def __init__(self, n: int, edgeList: List[List[int]]):
        """
        Interview explanation:
        Premium design (online 1697). Build MST then binary-lift max-edge on paths
        so each query(p,q,limit) checks whether that max is strictly < limit.

        Algorithm:
        - Kruskal MST; rooted forest; up/mx binary lifting tables; component UF.

        Complexity: O(E log E + N log N) init.
        """
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        edges = sorted(edgeList, key=lambda e: e[2])
        g = [[] for _ in range(n)]
        for u, v, w in edges:
            ru, rv = find(u), find(v)
            if ru == rv:
                continue
            parent[rv] = ru
            g[u].append((v, w))
            g[v].append((u, w))

        LOG = max(1, n.bit_length())
        up = [[0] * n for _ in range(LOG)]
        mx = [[0] * n for _ in range(LOG)]
        depth = [0] * n
        seen = [False] * n
        for root in range(n):
            if seen[root]:
                continue
            stack = [root]
            seen[root] = True
            up[0][root] = root
            while stack:
                u = stack.pop()
                for v, w in g[u]:
                    if seen[v]:
                        continue
                    seen[v] = True
                    depth[v] = depth[u] + 1
                    up[0][v] = u
                    mx[0][v] = w
                    stack.append(v)

        for k in range(1, LOG):
            for v in range(n):
                p = up[k - 1][v]
                up[k][v] = up[k - 1][p]
                mx[k][v] = max(mx[k - 1][v], mx[k - 1][p])

        self.up = up
        self.mx = mx
        self.depth = depth
        self.LOG = LOG
        self.comp = parent
        self.find = find

    def query(self, p: int, q: int, limit: int) -> bool:
        """
        Interview explanation:
        True iff p and q connected and every MST-path edge weight < limit
        (i.e. path max edge < limit).

        Algorithm:
        - Component check; binary-lift to compute path max edge.

        Complexity: O(log n) time.
        """
        if self.find(p) != self.find(q):
            return False
        if p == q:
            return True
        up, mx, depth, LOG = self.up, self.mx, self.depth, self.LOG
        best = 0
        if depth[p] < depth[q]:
            p, q = q, p
        diff = depth[p] - depth[q]
        bit = 0
        while diff:
            if diff & 1:
                best = max(best, mx[bit][p])
                p = up[bit][p]
            diff >>= 1
            bit += 1
        if p == q:
            return best < limit
        for k in range(LOG - 1, -1, -1):
            if up[k][p] != up[k][q]:
                best = max(best, mx[k][p], mx[k][q])
                p = up[k][p]
                q = up[k][q]
        best = max(best, mx[0][p], mx[0][q])
        return best < limit


# Your DistanceLimitedPathsExist object will be instantiated and called as such:
# obj = DistanceLimitedPathsExist(n, edgeList)
# param_1 = obj.query(p, q, limit)
# @lc code=end
