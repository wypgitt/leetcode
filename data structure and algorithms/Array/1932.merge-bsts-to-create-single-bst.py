#
# @lc app=leetcode id=1932 lang=python3
#
# [1932] Merge BSTs to Create Single BST
#
# https://leetcode.com/problems/merge-bsts-to-create-single-bst/description/
#
# algorithms
# Hard (39.53%)
# Likes:    675
# Dislikes: 49
# Total Accepted:    17.9K
# Total Submissions: 45.2K
# Testcase Example:  "[[2,1],[3,2,5],[5,4]]"
#
# You are given n BST (binary search tree) root nodes for n separate BSTs
# stored in an array trees (0-indexed). Each BST in trees has at most 3 nodes,
# and no two roots have the same value. In one operation, you can:
#
# Select two distinct indices i and j such that the value stored at one of the
# leaves of trees[i] is equal to the root value of trees[j].
#
# Replace the leaf node in trees[i] with trees[j].
#
# Remove trees[j] from trees.
#
# Return the root of the resulting BST if it is possible to form a valid BST
# after performing n - 1 operations, or null if it is impossible to create a
# valid BST.
#
# A BST (binary search tree) is a binary tree where each node satisfies the
# following property:
#
# Every node in the node's left subtree has a value strictly less than the
# node's value.
#
# Every node in the node's right subtree has a value strictly greater than the
# node's value.
#
# A leaf is a node that has no children.
#
# Example 1:
#
# Input: trees = [[2,1],[3,2,5],[5,4]]
# Output: [3,2,5,1,null,4]
# Explanation:
# In the first operation, pick i=1 and j=0, and merge trees[0] into trees[1].
# Delete trees[0], so trees = [[3,2,5,1],[5,4]].
#
# In the second operation, pick i=0 and j=1, and merge trees[1] into trees[0].
# Delete trees[1], so trees = [[3,2,5,1,null,4]].
#
# The resulting tree, shown above, is a valid BST, so return its root.
#
# Example 2:
#
# Input: trees = [[5,3,8],[3,2,6]]
# Output: []
# Explanation:
# Pick i=0 and j=1 and merge trees[1] into trees[0].
# Delete trees[1], so trees = [[5,3,8,2,6]].
#
# The resulting tree is shown above. This is the only valid operation that can
# be performed, but the resulting tree is not a valid BST, so return null.
#
# Example 3:
#
# Input: trees = [[5,4],[3]]
# Output: []
# Explanation: It is impossible to perform any operations.
#
# Constraints:
#
# n == trees.length
#
# 1 <= n <= 5 * 10^4
#
# The number of nodes in each tree is in the range [1, 3].
#
# Each node in the input may have children but no grandchildren.
#
# No two roots of trees have the same value.
#
# All the trees in the input are valid BSTs.
#
# 1 <= TreeNode.val <= 5 * 10^4.
#

# @lc code=start
from typing import List, Optional, Dict

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        """
        Interview explanation:
        Standard BST node used by merge input trees.

        Algorithm:
        - Store val and optional left/right child pointers.

        Complexity: O(1).
        """
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def canMerge(self, trees: List[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Merge BSTs by replacing a leaf valued x with the unique tree rooted at x.
        Exactly one overall root (never appears as another's leaf). Final tree
        must be a valid BST and include every node value exactly once.

        Algorithm:
        - Index roots by value; count how often each root value appears as a leaf.
          Unique indegree-0 root is candidate. DFS attach: when visiting a leaf
          whose value is a root, splice that tree in. Validate BST bounds and
          that count of traversed nodes equals total unique values.

        Complexity: O(N) time/space.
        """
        nodes: Dict[int, TreeNode] = {t.val: t for t in trees}
        indeg = {t.val: 0 for t in trees}
        for t in trees:
            for ch in (t.left, t.right):
                if ch and ch.val in nodes:
                    indeg[ch.val] += 1

        candidates = [nodes[v] for v, d in indeg.items() if d == 0]
        if len(candidates) != 1:
            return None
        root = candidates[0]

        vals = set()
        for t in trees:
            stack = [t]
            while stack:
                u = stack.pop()
                vals.add(u.val)
                if u.left:
                    stack.append(u.left)
                if u.right:
                    stack.append(u.right)

        self.cnt = 0

        def dfs(node: TreeNode, lo: float, hi: float) -> bool:
            if not node or not (lo < node.val < hi):
                return False
            self.cnt += 1
            left, right = node.left, node.right
            if left and left.val in nodes and left.val != node.val:
                left = nodes[left.val]
            if right and right.val in nodes and right.val != node.val:
                right = nodes[right.val]
            node.left, node.right = left, right
            if left and not dfs(left, lo, node.val):
                return False
            if right and not dfs(right, node.val, hi):
                return False
            return True

        if not dfs(root, float("-inf"), float("inf")):
            return None
        return root if self.cnt == len(vals) else None
# @lc code=end
