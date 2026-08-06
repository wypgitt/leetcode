#
# @lc app=leetcode id=113 lang=python3
#
# [113] Path Sum II
#
# https://leetcode.com/problems/path-sum-ii/description/
#
# algorithms
# Medium (62.16%)
# Likes:    8654
# Dislikes: 171
# Total Accepted:    1.2M
# Total Submissions: 1.9M
# Testcase Example:  '[5,4,8,11,null,13,4,7,2,null,null,5,1]\n22'
#
# Given the root of a binary tree and an integer targetSum, return all
# root-to-leaf paths where the sum of the node values in the path equals
# targetSum. Each path should be returned as a list of the node values, not
# node references.
# 
# A root-to-leaf path is a path starting from the root and ending at any leaf
# node. A leaf is a node with no children.
# 
# 
# Example 1:
# 
# 
# Input: root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
# Output: [[5,4,11,2],[5,8,4,5]]
# Explanation: There are two paths whose sum equals targetSum:
# 5 + 4 + 11 + 2 = 22
# 5 + 8 + 4 + 5 = 22
# 
# 
# Example 2:
# 
# 
# Input: root = [1,2,3], targetSum = 5
# Output: []
# 
# 
# Example 3:
# 
# 
# Input: root = [1,2], targetSum = 0
# Output: []
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [0, 5000].
# -1000 <= Node.val <= 1000
# -1000 <= targetSum <= 1000
# 
# 
#

# @lc code=start
from typing import List, Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        """
        Interview explanation:
        This is root-to-leaf path backtracking. A path list stores the current
        route, and the remaining sum tracks how much is still needed. At a leaf,
        the path is valid exactly when remaining equals the leaf value.

        Edge cases and tests:
        - Empty tree returns [].
        - Negative values are allowed, so do not prune by remaining < 0.
        - Only root-to-leaf paths count; partial paths ending at internal nodes
          are not answers.

        Complexity: O(n*h) worst-case for copying valid paths, O(h) recursion
        space excluding output.
        """
        ans = []
        path = []

        def dfs(node: Optional[TreeNode], remain: int) -> None:
            if not node:
                return
            path.append(node.val)
            remain -= node.val
            if not node.left and not node.right and remain == 0:
                ans.append(path.copy())
            else:
                dfs(node.left, remain)
                dfs(node.right, remain)
            path.pop()

        dfs(root, targetSum)
        return ans
# @lc code=end


