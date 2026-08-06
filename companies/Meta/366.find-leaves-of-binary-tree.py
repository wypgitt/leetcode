#
# @lc app=leetcode id=366 lang=python3
#
# [366] Find Leaves of Binary Tree
#
# https://leetcode.com/problems/find-leaves-of-binary-tree/description/
#
# algorithms
# Medium (81.36%)
# Likes:    3309
# Dislikes: 64
# Total Accepted:    291K
# Total Submissions: 357.7K
# Testcase Example:  "[1,2,3,4,5]"
#
#
# Given the root of a binary tree, collect a tree's nodes as if you were
# doing this:
#
# Collect all the leaf nodes.
#
# Remove all the leaf nodes.
#
# Repeat until the tree is empty.
#
# Example 1:
#
# Input: root = [1,2,3,4,5]
# Output: [[4,5,3],[2],[1]]
# Explanation:
# [[3,5,4],[2],[1]] and [[3,4,5],[2],[1]] are also considered correct
# answers since per each level it does not matter the order on which
# elements are returned.
#
# Example 2:
#
# Input: root = [1]
# Output: [[1]]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 100].
#
# -100 <= Node.val <= 100
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
    def findLeaves(self, root: Optional[TreeNode]) -> List[List[int]]:
        """
        Interview explanation:
        Group nodes by "height from leaves": height(leaf)=0; height(node)=
        1+max(children). Append node.val into groups[height].

        Algorithm:
        - DFS returns height; ensure groups list is long enough; append.
        - Return groups.

        Complexity: O(n) time, O(n) space.
        """
        groups: List[List[int]] = []

        def dfs(node: Optional[TreeNode]) -> int:
            if not node:
                return -1
            h = 1 + max(dfs(node.left), dfs(node.right))
            if h == len(groups):
                groups.append([])
            groups[h].append(node.val)
            return h

        dfs(root)
        return groups
# @lc code=end
