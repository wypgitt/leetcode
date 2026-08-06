#
# @lc app=leetcode id=965 lang=python3
#
# [965] Univalued Binary Tree
#
# https://leetcode.com/problems/univalued-binary-tree/description/
#
# algorithms
# Easy (73.26%)
# Likes:    1995
# Dislikes: 68
# Total Accepted:    284K
# Total Submissions: 388K
# Testcase Example:  "[1,1,1,1,1,null,1]"
#
# A binary tree is uni-valued if every node in the tree has the same value.
#
# Given the root of a binary tree, return true if the given tree is uni-valued,
# or false otherwise.
#
# Example 1:
#
# Input: root = [1,1,1,1,1,null,1]
# Output: true
#
# Example 2:
#
# Input: root = [2,2,2,5,2]
# Output: false
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 100].
#
# 0 <= Node.val < 100
#

# @lc code=start
from collections import deque
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def isUnivalTree(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        All nodes must equal root.val. DFS: False on mismatch; True if both
        subtrees univalued with same value.

        Algorithm (DFS):
        - val = root.val
        - dfs(node): if not node: True; if node.val!=val: False;
          return dfs(left) and dfs(right)

        Complexity: O(n) time, O(h) space.
        """
        if not root:
            return True
        val = root.val

        def dfs(node: Optional[TreeNode]) -> bool:
            if not node:
                return True
            if node.val != val:
                return False
            return dfs(node.left) and dfs(node.right)

        return dfs(root)

    def isUnivalTree_bfs(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Alternate: BFS/queue; every dequeued node must equal root.val.

        Algorithm (BFS):
        - q=[root]; v=root.val
        - While q: node=pop; if val!=v False; enqueue children

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return True
        v = root.val
        q = deque([root])
        while q:
            node = q.popleft()
            if node.val != v:
                return False
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        return True
# @lc code=end

