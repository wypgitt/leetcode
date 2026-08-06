#
# @lc app=leetcode id=1305 lang=python3
#
# [1305] All Elements in Two Binary Search Trees
#
# https://leetcode.com/problems/all-elements-in-two-binary-search-trees/description/
#
# algorithms
# Medium (80.37%)
# Likes:    3201
# Dislikes: 99
# Total Accepted:    270K
# Total Submissions: 336K
# Testcase Example:  "[2,1,4]"
#
# Given two binary search trees root1 and root2, return a list containing all
# the integers from both trees sorted in ascending order.
#
# Example 1:
#
# Input: root1 = [2,1,4], root2 = [1,0,3]
# Output: [0,1,1,2,3,4]
#
# Example 2:
#
# Input: root1 = [1,null,8], root2 = [8,1]
# Output: [1,1,8,8]
#
# Constraints:
#
# The number of nodes in each tree is in the range [0, 5000].
#
# -10^5 <= Node.val <= 10^5
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
    def getAllElements(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        BST inorder is sorted. Inorder both trees then merge two sorted arrays
        (classic merge step) for a globally sorted list.

        Algorithm (inorder + merge):
        - Inorder into a,b; two-pointer merge.

        Complexity: O(n+m) time, O(n+m) space.
        """
        def inorder(node, out):
            if not node:
                return
            inorder(node.left, out)
            out.append(node.val)
            inorder(node.right, out)

        a, b = [], []
        inorder(root1, a)
        inorder(root2, b)
        i = j = 0
        ans = []
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                ans.append(a[i])
                i += 1
            else:
                ans.append(b[j])
                j += 1
        ans.extend(a[i:])
        ans.extend(b[j:])
        return ans

    def getAllElements_sort(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Alternate: flatten both trees and sort. Simpler; worse asymptotics than
        merge of inorders.

        Algorithm:
        - DFS collect; return sorted(vals).

        Complexity: O((n+m) log(n+m)) time, O(n+m) space.
        """
        vals = []

        def dfs(node):
            if not node:
                return
            vals.append(node.val)
            dfs(node.left)
            dfs(node.right)

        dfs(root1)
        dfs(root2)
        return sorted(vals)
# @lc code=end

