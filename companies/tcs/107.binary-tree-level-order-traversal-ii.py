#
# @lc app=leetcode id=107 lang=python3
#
# [107] Binary Tree Level Order Traversal II
#
# https://leetcode.com/problems/binary-tree-level-order-traversal-ii/description/
#
# algorithms
# Medium (68.15%)
# Likes:    5187
# Dislikes: 335
# Total Accepted:    835.4K
# Total Submissions: 1.2M
# Testcase Example:  '[3,9,20,null,null,15,7]'
#
# Given the root of a binary tree, return the bottom-up level order traversal
# of its nodes' values. (i.e., from left to right, level by level from leaf to
# root).
# 
# 
# Example 1:
# 
# 
# Input: root = [3,9,20,null,null,15,7]
# Output: [[15,7],[9,20],[3]]
# 
# 
# Example 2:
# 
# 
# Input: root = [1]
# Output: [[1]]
# 
# 
# Example 3:
# 
# 
# Input: root = []
# Output: []
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [0, 2000].
# -1000 <= Node.val <= 1000
# 
# 
#

# @lc code=start
from typing import List, Optional
from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def levelOrderBottom(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Interview explanation:
        Perform standard BFS to collect levels from top to bottom, then reverse
        the list of levels. BFS is still the best fit because it naturally groups
        nodes by depth using a queue.

        Edge cases and tests:
        - Empty tree returns [].
        - Single node remains [[value]].
        - Uneven depth is fine because each level uses the queue size snapshot.

        Complexity: O(n) time, O(w) queue space plus output.
        """
        if not root:
            return []
        levels = []
        q = deque([root])
        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            levels.append(level)
        return levels[::-1]
# @lc code=end


