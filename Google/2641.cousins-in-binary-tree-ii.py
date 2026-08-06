#
# @lc app=leetcode id=2641 lang=python3
#
# [2641] Cousins in Binary Tree II
#
# https://leetcode.com/problems/cousins-in-binary-tree-ii/description/
#
# algorithms
# Medium (75.94%)
# Likes:    1242
# Dislikes: 54
# Total Accepted:    132K
# Total Submissions: 173.8K
# Testcase Example:  "[5,4,9,1,10,null,7]"
#
# Given the root of a binary tree, replace the value of each node in the tree
# with the sum of all its cousins' values.
#
# Two nodes of a binary tree are cousins if they have the same depth with
# different parents.
#
# Return the root of the modified tree.
#
# Note that the depth of a node is the number of edges in the path from the root
# node to it.
#
#
#
# Example 1:
#
# Input: root = [5,4,9,1,10,null,7]
# Output: [0,0,0,7,7,null,11]
# Explanation: The diagram above shows the initial binary tree and the binary
# tree after changing the value of each node.
# - Node with value 5 does not have any cousins so its sum is 0.
# - Node with value 4 does not have any cousins so its sum is 0.
# - Node with value 9 does not have any cousins so its sum is 0.
# - Node with value 1 has a cousin with value 7 so its sum is 7.
# - Node with value 10 has a cousin with value 7 so its sum is 7.
# - Node with value 7 has cousins with values 1 and 10 so its sum is 11.
#
# Example 2:
#
# Input: root = [3,1,2]
# Output: [0,0,0]
# Explanation: The diagram above shows the initial binary tree and the binary
# tree after changing the value of each node.
# - Node with value 3 does not have any cousins so its sum is 0.
# - Node with value 1 does not have any cousins so its sum is 0.
# - Node with value 2 does not have any cousins so its sum is 0.
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is in the range [1, 10^5].
#
#
# 1 <= Node.val <= 10^4
#

# @lc code=start
from typing import Optional
from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def replaceValueInTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Replace each node with the sum of its cousins (same depth, different
        parent). Equivalent to level_sum - sibling_group_sum.

        Algorithm:
        - BFS by parent level; sum next-level values, then set each child to
          that sum minus its sibling pair sum. Root becomes 0.

        Complexity: O(n) time, O(w) space.
        """
        if not root:
            return root
        root.val = 0
        q = deque([root])
        while q:
            level_sum = 0
            for node in q:
                if node.left:
                    level_sum += node.left.val
                if node.right:
                    level_sum += node.right.val
            for _ in range(len(q)):
                node = q.popleft()
                sibling = 0
                if node.left:
                    sibling += node.left.val
                if node.right:
                    sibling += node.right.val
                if node.left:
                    node.left.val = level_sum - sibling
                    q.append(node.left)
                if node.right:
                    node.right.val = level_sum - sibling
                    q.append(node.right)
        return root

    def replaceValueInTree_dfs(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Alternate DFS: first collect per-depth sums, then rewrite each node as
        level_sum - sibling_group_sum.

        Algorithm:
        - dfs1 accumulate level sums; dfs2 pass sibling sum and assign values.

        Complexity: O(n) time, O(h) space.
        """
        if not root:
            return root
        level_sums: list[int] = []

        def dfs1(node: Optional[TreeNode], d: int) -> None:
            if not node:
                return
            if d == len(level_sums):
                level_sums.append(0)
            level_sums[d] += node.val
            dfs1(node.left, d + 1)
            dfs1(node.right, d + 1)

        def dfs2(node: Optional[TreeNode], d: int, sibling_sum: int) -> None:
            if not node:
                return
            node.val = level_sums[d] - sibling_sum
            child_sum = (node.left.val if node.left else 0) + (
                node.right.val if node.right else 0
            )
            dfs2(node.left, d + 1, child_sum)
            dfs2(node.right, d + 1, child_sum)

        dfs1(root, 0)
        dfs2(root, 0, root.val)
        return root
# @lc code=end
