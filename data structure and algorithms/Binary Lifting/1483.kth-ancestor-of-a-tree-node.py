#
# @lc app=leetcode id=1483 lang=python3
#
# [1483] Kth Ancestor of a Tree Node
#
# https://leetcode.com/problems/kth-ancestor-of-a-tree-node/description/
#
# algorithms
# Hard (39.32%)
# Likes:    2170
# Dislikes: 127
# Total Accepted:    60.3K
# Total Submissions: 153K
# Testcase Example:  "[\"TreeAncestor\",\"getKthAncestor\",\"getKthAncestor\",\"getKthAncestor\"]"
#
# You are given a tree with n nodes numbered from 0 to n - 1 in the form of a
# parent array parent where parent[i] is the parent of i^th node. The root of
# the tree is node 0. Find the k^th ancestor of a given node.
#
# The k^th ancestor of a tree node is the k^th node in the path from that node
# to the root node.
#
# Implement the TreeAncestor class:
#
# TreeAncestor(int n, int[] parent) Initializes the object with the number of
# nodes in the tree and the parent array.
#
# int getKthAncestor(int node, int k) return the k^th ancestor of the given
# node node. If there is no such ancestor, return -1.
#
# Example 1:
#
# Input
# ["TreeAncestor", "getKthAncestor", "getKthAncestor", "getKthAncestor"]
# [[7, [-1, 0, 0, 1, 1, 2, 2]], [3, 1], [5, 2], [6, 3]]
# Output
# [null, 1, 0, -1]
#
# Explanation
# TreeAncestor treeAncestor = new TreeAncestor(7, [-1, 0, 0, 1, 1, 2, 2]);
# treeAncestor.getKthAncestor(3, 1); // returns 1 which is the parent of 3
# treeAncestor.getKthAncestor(5, 2); // returns 0 which is the grandparent of 5
# treeAncestor.getKthAncestor(6, 3); // returns -1 because there is no such
# ancestor
#
# Constraints:
#
# 1 <= k <= n <= 5 * 10^4
#
# parent.length == n
#
# parent[0] == -1
#
# 0 <= parent[i] < n for all 0 < i < n
#
# 0 <= node < n
#
# There will be at most 5 * 10^4 queries.
#

# @lc code=start
from typing import List


class TreeAncestor:
    def __init__(self, n: int, parent: List[int]):
        """
        Interview explanation:
        Answer k-th ancestor queries. Binary lifting: up[j][i] = 2^j-th ancestor
        of i. Precompute from parent array.

        Algorithm:
        - LOG ~ 16 for n<=5e4; up[0]=parent; up[j][i]=up[j-1][up[j-1][i]].

        Complexity: O(n log n) preprocess, O(n log n) space.
        """
        self.parent = parent
        self.LOG = 16
        self.up = [[-1] * n for _ in range(self.LOG)]
        for i in range(n):
            self.up[0][i] = parent[i]
        for j in range(1, self.LOG):
            for i in range(n):
                p = self.up[j - 1][i]
                if p != -1:
                    self.up[j][i] = self.up[j - 1][p]

    def getKthAncestor(self, node: int, k: int) -> int:
        """
        Interview explanation:
        Jump by bits of k using binary lifting table.

        Algorithm:
        - For bit b in k: if set, node = up[b][node]; stop if -1.

        Complexity: O(log k) per query.
        """
        for b in range(self.LOG):
            if k & (1 << b):
                node = self.up[b][node]
                if node == -1:
                    return -1
        return node


# Your TreeAncestor object will be instantiated and called as such:
# obj = TreeAncestor(n, parent)
# param_1 = obj.getKthAncestor(node,k)

    def getKthAncestor_naive(self, node: int, k: int) -> int:
        """
        Interview explanation:
        Alternate: climb parent pointer k times (slow; fine for light queries).

        Algorithm:
        - For _ in range(k): node=parent[node]; return -1 if becomes -1.

        Complexity: O(k) per query, O(n) space for parent.
        """
        for _ in range(k):
            if node == -1:
                return -1
            node = self.parent[node]
        return node

# @lc code=end
