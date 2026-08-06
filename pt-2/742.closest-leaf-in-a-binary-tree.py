#
# @lc app=leetcode id=742 lang=python3
#
# [742] Closest Leaf in a Binary Tree
#
# https://leetcode.com/problems/closest-leaf-in-a-binary-tree/description/
#
# algorithms
# Medium (47.43%)
# Likes:    890
# Dislikes: 190
# Total Accepted:    56.1K
# Total Submissions: 118.2K
# Testcase Example:  '[1,3,2]\n1'
#
# Given the root of a binary tree where every node has a unique value and a
# target integer k, return the value of the nearest leaf node to the target k
# in the tree.
# 
# Nearest to a leaf means the least number of edges traveled on the binary tree
# to reach any leaf of the tree. Also, a node is called a leaf if it has no
# children.
# 
# 
# Example 1:
# 
# 
# Input: root = [1,3,2], k = 1
# Output: 2
# Explanation: Either 2 or 3 is the nearest leaf node to the target of 1.
# 
# 
# Example 2:
# 
# 
# Input: root = [1], k = 1
# Output: 1
# Explanation: The nearest leaf node is the root node itself.
# 
# 
# Example 3:
# 
# 
# Input: root = [1,2,3,4,null,null,null,5,null,6], k = 2
# Output: 3
# Explanation: The leaf node with value 3 (and not the leaf node with value 6)
# is nearest to the node with value 2.
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 1000].
# 1 <= Node.val <= 1000
# All the values of the tree are unique.
# There exist some node in the tree where Node.val == k.
# 
# 
#

# @lc code=start
from collections import defaultdict, deque
from typing import Optional


class Solution:
    def findClosestLeaf(self, root: Optional['TreeNode'], k: int) -> int:
        graph = defaultdict(list)
        target = None

        def build(node, parent=None):
            nonlocal target
            if not node:
                return
            if node.val == k:
                target = node
            if parent:
                graph[node].append(parent)
                graph[parent].append(node)
            build(node.left, node)
            build(node.right, node)

        build(root)
        q = deque([target])
        seen = {target}
        while q:
            node = q.popleft()
            if not node.left and not node.right:
                return node.val
            for nei in graph[node]:
                if nei not in seen:
                    seen.add(nei)
                    q.append(nei)
        return root.val
# @lc code=end

"""
Interview explanation:
The closest leaf may be below k or above it through an ancestor and then down another branch. Convert the tree into an undirected graph using parent links, then BFS from the target node. The first leaf reached is closest by edge count.

Data structure: adjacency list keyed by TreeNode objects and a BFS queue.

Edge cases: if k itself is a leaf, BFS returns it immediately. A single-node tree also returns the root value.

Complexity: building the graph is O(n), BFS is O(n), and space is O(n).
"""
