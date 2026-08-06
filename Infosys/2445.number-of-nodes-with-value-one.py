#
# @lc app=leetcode id=2445 lang=python3
#
# [2445] Number of Nodes With Value One
#
# https://leetcode.com/problems/number-of-nodes-with-value-one/description/
#
# algorithms
# Medium (65.98%)
# Likes:    82
# Dislikes: 10
# Total Accepted:    3K
# Total Submissions: 4.6K
# Testcase Example:  "5\n[1,2,5]"
#
#
# There is an undirected connected tree with n nodes labeled from 1 to n
# and n - 1 edges. You are given the integer n. The parent node of a node
# with a label v is the node with the label floor (v / 2). The root of the
# tree is the node with the label 1.
#
# For example, if n = 7, then the node with the label 3 has the node with
# the label floor(3 / 2) = 1 as its parent, and the node with the label 7
# has the node with the label floor(7 / 2) = 3 as its parent.
#
# You are also given an integer array queries. Initially, every node has a
# value 0 on it. For each query queries[i], you should flip all values in
# the subtree of the node with the label queries[i].
#
# Return the total number of nodes with the value 1 after processing all
# the queries.
#
# Note that:
#
# Flipping the value of a node means that the node with the value 0
# becomes 1 and vice versa.
#
# floor(x) is equivalent to rounding x down to the nearest integer.
#
# Example 1:
#
# Input: n = 5 , queries = [1,2,5]
# Output: 3
# Explanation: The diagram above shows the tree structure and its status
# after performing the queries. The blue node represents the value 0, and
# the red node represents the value 1.
# After processing the queries, there are three red nodes (nodes with
# value 1): 1, 3, and 5.
#
# Example 2:
#
# Input: n = 3, queries = [2,3,3]
# Output: 1
# Explanation: The diagram above shows the tree structure and its status
# after performing the queries. The blue node represents the value 0, and
# the red node represents the value 1.
# After processing the queries, there are one red node (node with value
# 1): 2.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 1 <= queries.length <= 10^5
#
# 1 <= queries[i] <= n
#
# @lc code=start
from typing import List


class Solution:
    def numberOfNodes(self, n: int, queries: List[int]) -> int:
        """
        Interview explanation:
        Premium. Tree nodes 1..n (children 2i,2i+1). Query flips a node and all
        descendants. Start at 0; count nodes with value 1.

        Algorithm:
        - Toggle mark[q] for each query; node value = XOR of marks on ancestors
          including itself (path from root).

        Complexity: O(n+q) time, O(n) space.
        """
        mark = [0] * (n + 1)
        for q in queries:
            mark[q] ^= 1
        ans = 0
        val = [0] * (n + 1)
        for u in range(1, n + 1):
            val[u] = mark[u] ^ (val[u // 2] if u > 1 else 0)
            ans += val[u]
        return ans
# @lc code=end
