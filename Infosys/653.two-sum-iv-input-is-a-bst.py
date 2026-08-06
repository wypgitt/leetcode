#
# @lc app=leetcode id=653 lang=python3
#
# [653] Two Sum IV - Input is a BST
#
# https://leetcode.com/problems/two-sum-iv-input-is-a-bst/description/
#
# algorithms
# Easy (63.58%)
# Likes:    7366
# Dislikes: 292
# Total Accepted:    803K
# Total Submissions: 1.3M
# Testcase Example:  "[5,3,6,2,4,null,7]"
#
# Given the root of a binary search tree and an integer k, return true if there
# exist two elements in the BST such that their sum is equal to k, or false
# otherwise.
#
# Example 1:
#
# Input: root = [5,3,6,2,4,null,7], k = 9
# Output: true
#
# Example 2:
#
# Input: root = [5,3,6,2,4,null,7], k = 28
# Output: false
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -10^4 <= Node.val <= 10^4
#
# root is guaranteed to be a valid binary search tree.
#
# -10^5 <= k <= 10^5
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
    def findTarget(self, root: Optional[TreeNode], k: int) -> bool:
        """
        Interview explanation:
        Two-sum in a BST: DFS with a seen set; for each node check if k-val seen.

        Algorithm:
        - DFS: if k-node.val in seen return True; add val; recurse children.

        Complexity: O(N) time, O(N) space.
        """
        seen = set()

        def dfs(node) -> bool:
            if not node:
                return False
            if k - node.val in seen:
                return True
            seen.add(node.val)
            return dfs(node.left) or dfs(node.right)

        return dfs(root)

    def findTarget_inorder(
        self, root: Optional[TreeNode], k: int
    ) -> bool:
        """
        Interview explanation:
        Alternate classic: inorder gives sorted array; two pointers L/R for
        two-sum.

        Algorithm:
        - Inorder collect vals; lo,hi while lo<hi compare sum to k.

        Complexity: O(N) time, O(N) space.
        """
        vals: List[int] = []

        def inorder(node):
            if not node:
                return
            inorder(node.left)
            vals.append(node.val)
            inorder(node.right)

        inorder(root)
        lo, hi = 0, len(vals) - 1
        while lo < hi:
            s = vals[lo] + vals[hi]
            if s == k:
                return True
            if s < k:
                lo += 1
            else:
                hi -= 1
        return False
# @lc code=end
