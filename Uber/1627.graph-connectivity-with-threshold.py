#
# @lc app=leetcode id=1627 lang=python3
#
# [1627] Graph Connectivity With Threshold
#
# https://leetcode.com/problems/graph-connectivity-with-threshold/description/
#
# algorithms
# Hard (49.79%)
# Likes:    615
# Dislikes: 34
# Total Accepted:    24.8K
# Total Submissions: 49.8K
# Testcase Example:  "6"
#
# We have n cities labeled from 1 to n. Two different cities with labels x and
# y are directly connected by a bidirectional road if and only if x and y share
# a common divisor strictly greater than some threshold. More formally, cities
# with labels x and y have a road between them if there exists an integer z
# such that all of the following are true:
#
# x % z == 0,
#
# y % z == 0, and
#
# z > threshold.
#
# Given the two integers, n and threshold, and an array of queries, you must
# determine for each queries[i] = [a_i, b_i] if cities a_i and b_i are
# connected directly or indirectly. (i.e. there is some path between them).
#
# Return an array answer, where answer.length == queries.length and answer[i]
# is true if for the i^th query, there is a path between a_i and b_i, or
# answer[i] is false if there is no path.
#
# Example 1:
#
# Input: n = 6, threshold = 2, queries = [[1,4],[2,5],[3,6]]
# Output: [false,false,true]
# Explanation: The divisors for each number:
# 1: 1
# 2: 1, 2
# 3: 1, 3
# 4: 1, 2, 4
# 5: 1, 5
# 6: 1, 2, 3, 6
# Using the underlined divisors above the threshold, only cities 3 and 6 share
# a common divisor, so they are the
# only ones directly connected. The result of each query:
# [1,4] 1 is not connected to 4
# [2,5] 2 is not connected to 5
# [3,6] 3 is connected to 6 through path 3--6
#
# Example 2:
#
# Input: n = 6, threshold = 0, queries = [[4,5],[3,4],[3,2],[2,6],[1,3]]
# Output: [true,true,true,true,true]
# Explanation: The divisors for each number are the same as the previous
# example. However, since the threshold is 0,
# all divisors can be used. Since all numbers share 1 as a divisor, all cities
# are connected.
#
# Example 3:
#
# Input: n = 5, threshold = 1, queries = [[4,5],[4,5],[3,2],[2,3],[3,4]]
# Output: [false,false,false,false,false]
# Explanation: Only cities 2 and 4 share a common divisor 2 which is strictly
# greater than the threshold 1, so they are the only ones directly connected.
# Please notice that there can be multiple queries for the same pair of nodes
# [x, y], and that the query [x, y] is equivalent to the query [y, x].
#
# Constraints:
#
# 2 <= n <= 10^4
#
# 0 <= threshold <= n
#
# 1 <= queries.length <= 10^5
#
# queries[i].length == 2
#
# 1 <= a_i, b_i <= cities
#
# a_i != b_i
#

# @lc code=start
from typing import List


class Solution:
    def areConnected(self, n: int, threshold: int, queries: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        Two cities connected if path exists where each edge gcd>threshold.
        Equivalent: Union-Find unite multiples of each d>threshold.

        Algorithm (Union-Find):
        - For d = threshold+1 .. n: unite d,2d,3d,...
        - Answer find(a)==find(b) for each query.

        Complexity: O(n log n + q α(n)) time.
        """
        parent = list(range(n + 1))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for d in range(threshold + 1, n + 1):
            for m in range(2 * d, n + 1, d):
                union(d, m)
        return [find(a) == find(b) for a, b in queries]

    def areConnected_dfs(self, n: int, threshold: int, queries: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        Alternate: build graph by connecting multiples then DFS/components labeling
        (same connectivity; UF preferred for large n).

        Algorithm (components):
        - Build adj via same multiples edges; DFS assign component ids; compare.

        Complexity: O(n log n + q) time, O(n log n) edges worst.
        """
        from collections import defaultdict

        g = defaultdict(list)
        for d in range(threshold + 1, n + 1):
            for m in range(2 * d, n + 1, d):
                g[d].append(m)
                g[m].append(d)
        comp = [0] * (n + 1)
        cid = 0
        for i in range(1, n + 1):
            if comp[i]:
                continue
            cid += 1
            st = [i]
            comp[i] = cid
            while st:
                u = st.pop()
                for v in g[u]:
                    if not comp[v]:
                        comp[v] = cid
                        st.append(v)
        return [comp[a] == comp[b] for a, b in queries]
# @lc code=end
