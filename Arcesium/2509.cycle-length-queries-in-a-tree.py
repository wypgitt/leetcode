#
# @lc app=leetcode id=2509 lang=python3
#
# [2509] Cycle Length Queries in a Tree
#
# https://leetcode.com/problems/cycle-length-queries-in-a-tree/description/
#
# algorithms
# Hard (60.79%)
# Likes:    397
# Dislikes: 31
# Total Accepted:    20.6K
# Total Submissions: 33.9K
# Testcase Example:  "3\n[[5,3],[4,7],[2,3]]"
#
# You are given an integer n. There is a complete binary tree with 2^n - 1
# nodes. The root of that tree is the node with the value 1, and every node with
# a value val in the range [1, 2^n - 1 - 1] has two children where:
#
#
# The left node has the value 2 * val, and
#
#
# The right node has the value 2 * val + 1.
#
# You are also given a 2D integer array queries of length m, where queries[i] =
# [a_i, b_i]. For each query, solve the following problem:
#
#
# Add an edge between the nodes with values a_i and b_i.
#
#
# Find the length of the cycle in the graph.
#
#
# Remove the added edge between nodes with values a_i and b_i.
#
# Note that:
#
#
# A cycle is a path that starts and ends at the same node, and each edge in the
# path is visited only once.
#
#
# The length of a cycle is the number of edges visited in the cycle.
#
#
# There could be multiple edges between two nodes in the tree after adding the
# edge of the query.
#
# Return an array answer of length m where answer[i] is the answer to the i^th
# query.
#
#
#
# Example 1:
#
# Input: n = 3, queries = [[5,3],[4,7],[2,3]]
# Output: [4,5,3]
# Explanation: The diagrams above show the tree of 2^3 - 1 nodes. Nodes colored
# in red describe the nodes in the cycle after adding the edge.
# - After adding the edge between nodes 3 and 5, the graph contains a cycle of
# nodes [5,2,1,3]. Thus answer to the first query is 4. We delete the added edge
# and process the next query.
# - After adding the edge between nodes 4 and 7, the graph contains a cycle of
# nodes [4,2,1,3,7]. Thus answer to the second query is 5. We delete the added
# edge and process the next query.
# - After adding the edge between nodes 2 and 3, the graph contains a cycle of
# nodes [2,1,3]. Thus answer to the third query is 3. We delete the added edge.
#
# Example 2:
#
# Input: n = 2, queries = [[1,2]]
# Output: [2]
# Explanation: The diagram above shows the tree of 2^2 - 1 nodes. Nodes colored
# in red describe the nodes in the cycle after adding the edge.
# - After adding the edge between nodes 1 and 2, the graph contains a cycle of
# nodes [2,1]. Thus answer for the first query is 2. We delete the added edge.
#
#
#
# Constraints:
#
#
# 2 <= n <= 30
#
#
# m == queries.length
#
#
# 1 <= m <= 10^5
#
#
# queries[i].length == 2
#
#
# 1 <= a_i, b_i <= 2^n - 1
#
#
# a_i != b_i
#

# @lc code=start
from typing import List


class Solution:
    def cycleLengthQueries(self, n: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Complete binary heap-tree (parent = val//2). Adding edge a-b creates a
        cycle of length dist(a,LCA)+dist(b,LCA)+1.

        Algorithm:
        - For each query, climb the larger node toward the root until a==b
          (implicit LCA); steps+1 is the cycle length.

        Complexity: O(m * n) time (n<=30), O(1) extra space besides answer.
        """
        ans = []
        for a, b in queries:
            steps = 0
            while a != b:
                if a > b:
                    a //= 2
                else:
                    b //= 2
                steps += 1
            ans.append(steps + 1)
        return ans

    def cycleLengthQueries_lca(self, n: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Explicit LCA via depth equalization then joint climb; cycle = depth(a) +
        depth(b) - 2*depth(lca) + 1.

        Algorithm:
        - depth(x)=floor(log2(x)); bring deeper node up to same depth, then climb
          together; same formula.

        Complexity: O(m * n) time, O(1) extra space.
        """
        def depth(x: int) -> int:
            return x.bit_length() - 1

        ans = []
        for a, b in queries:
            da, db = depth(a), depth(b)
            aa, bb = a, b
            if da > db:
                for _ in range(da - db):
                    aa //= 2
            else:
                for _ in range(db - da):
                    bb //= 2
            while aa != bb:
                aa //= 2
                bb //= 2
            lca = aa
            ans.append(da + db - 2 * depth(lca) + 1)
        return ans
# @lc code=end
