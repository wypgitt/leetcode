#
# @lc app=leetcode id=655 lang=python3
#
# [655] Print Binary Tree
#
# https://leetcode.com/problems/print-binary-tree/description/
#
# algorithms
# Medium (66.57%)
# Likes:    570
# Dislikes: 470
# Total Accepted:    86.9K
# Total Submissions: 130.5K
# Testcase Example:  '[1,2]'
#
# Given the root of a binary tree, construct a 0-indexed m x n string matrix
# res that represents a formatted layout of the tree. The formatted layout
# matrix should be constructed using the following rules:
# 
# 
# The height of the tree is height and the number of rows m should be equal to
# height + 1.
# The number of columns n should be equal to 2^height+1 - 1.
# Place the root node in the middle of the top row (more formally, at location
# res[0][(n-1)/2]).
# For each node that has been placed in the matrix at position res[r][c], place
# its left child at res[r+1][c-2^height-r-1] and its right child at
# res[r+1][c+2^height-r-1].
# Continue this process until all the nodes in the tree have been placed.
# Any empty cells should contain the empty string "".
# 
# 
# Return the constructed matrix res.
# 
# 
# Example 1:
# 
# 
# Input: root = [1,2]
# Output: 
# [["","1",""],
# ["2","",""]]
# 
# 
# Example 2:
# 
# 
# Input: root = [1,2,3,null,4]
# Output: 
# [["","","","1","","",""],
# ["","2","","","","3",""],
# ["","","4","","","",""]]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 2^10].
# -99 <= Node.val <= 99
# The depth of the tree will be in the range [1, 10].
# 
# 
#

# @lc code=start
from typing import List, Optional


class Solution:
    def printTree(self, root: Optional['TreeNode']) -> List[List[str]]:
        def height(node):
            if not node:
                return 0
            return 1 + max(height(node.left), height(node.right))

        h = height(root)
        rows, cols = h, 2 ** h - 1
        ans = [[''] * cols for _ in range(rows)]

        def place(node, r, lo, hi):
            if not node:
                return
            mid = (lo + hi) // 2
            ans[r][mid] = str(node.val)
            place(node.left, r + 1, lo, mid - 1)
            place(node.right, r + 1, mid + 1, hi)

        place(root, 0, 0, cols - 1)
        return ans
# @lc code=end

"""
Interview explanation:
A tree of height h needs h rows and 2^h - 1 columns. Place each node in the middle of its assigned column range; its left child gets the left half and its right child gets the right half.

Data structure: a 2D list of strings is the required output grid.

Edge cases: missing children leave empty strings. The midpoint placement works for negative and multi-digit values because each cell stores a string.

Complexity: computing height is O(n), filling nodes is O(n), and initializing the grid costs O(h * 2^h). Output space is O(h * 2^h).
"""
