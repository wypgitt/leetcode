#
# @lc app=leetcode id=2196 lang=python3
#
# [2196] Create Binary Tree From Descriptions
#
# https://leetcode.com/problems/create-binary-tree-from-descriptions/description/
#
# algorithms
# Medium (83.91%)
# Likes:    1914
# Dislikes: 44
# Total Accepted:    270K
# Total Submissions: 321.7K
# Testcase Example:  "[[20,15,1],[20,17,0],[50,20,1],[50,80,0],[80,19,1]]"
#
# You are given a 2D integer array descriptions where descriptions[i] =
# [parent_i, child_i, isLeft_i] indicates that parent_i is the parent of child_i
# in a binary tree of unique values. Furthermore,
#
#
# If isLeft_i == 1, then child_i is the left child of parent_i.
#
#
# If isLeft_i == 0, then child_i is the right child of parent_i.
#
# Construct the binary tree described by descriptions and return its root.
#
# The test cases will be generated such that the binary tree is valid.
#
#
#
# Example 1:
#
# Input: descriptions = [[20,15,1],[20,17,0],[50,20,1],[50,80,0],[80,19,1]]
# Output: [50,20,80,15,17,19]
# Explanation: The root node is the node with value 50 since it has no parent.
# The resulting binary tree is shown in the diagram.
#
# Example 2:
#
# Input: descriptions = [[1,2,1],[2,3,0],[3,4,1]]
# Output: [1,2,null,null,3,4]
# Explanation: The root node is the node with value 1 since it has no parent.
# The resulting binary tree is shown in the diagram.
#
#
#
# Constraints:
#
#
# 1 <= descriptions.length <= 10^4
#
#
# descriptions[i].length == 3
#
#
# 1 <= parent_i, child_i <= 10^5
#
#
# 0 <= isLeft_i <= 1
#
#
# The binary tree described by descriptions is valid.
#

# @lc code=start
from typing import List, Optional

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
    def createBinaryTree(self, descriptions: List[List[int]]) -> Optional[TreeNode]:
        """
        Interview explanation:
        descriptions[i] = [parent, child, isLeft]. Build the binary tree; return
        root (the unique node that never appears as a child).

        Algorithm:
        (hash map of nodes)
        - Create/get TreeNode for each id; link left/right; track children set;
          root = node not in children.

        Complexity: O(n) time, O(n) space.
        """
        nodes = {}
        children = set()
        for p, c, is_left in descriptions:
            if p not in nodes:
                nodes[p] = TreeNode(p)
            if c not in nodes:
                nodes[c] = TreeNode(c)
            if is_left:
                nodes[p].left = nodes[c]
            else:
                nodes[p].right = nodes[c]
            children.add(c)
        for v, node in nodes.items():
            if v not in children:
                return node
        return None
# @lc code=end
