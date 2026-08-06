#
# @lc app=leetcode id=663 lang=python3
#
# [663] Equal Tree Partition
#
# https://leetcode.com/problems/equal-tree-partition/description/
#
# algorithms
# Medium (42.30%)
# Likes:    509
# Dislikes: 37
# Total Accepted:    36.8K
# Total Submissions: 87.1K
# Testcase Example:  '[5,10,10,null,null,2,3]'
#
# Given the root of a binary tree, return true if you can partition the tree
# into two trees with equal sums of values after removing exactly one edge on
# the original tree.
# 
# 
# Example 1:
# 
# 
# Input: root = [5,10,10,null,null,2,3]
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: root = [1,2,10,null,null,2,20]
# Output: false
# Explanation: You cannot split the tree into two trees with equal sums after
# removing exactly one edge on the tree.
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 10^4].
# -10^5 <= Node.val <= 10^5
# 
# 
#

# @lc code=start
from typing import Optional


class Solution:
    def checkEqualTree(self, root: Optional['TreeNode']) -> bool:
        sums = []

        def dfs(node):
            if not node:
                return 0
            total = node.val + dfs(node.left) + dfs(node.right)
            sums.append(total)
            return total

        total = dfs(root)
        sums.pop()  # cannot cut above the original root
        return total % 2 == 0 and total // 2 in sums
# @lc code=end

"""
Interview explanation:
Cutting one edge separates one child subtree from the rest. The two parts are equal exactly when some non-root subtree has sum total/2. Compute every subtree sum with postorder DFS.

Data structure: a list stores subtree sums; the root sum is removed because it is not a valid cut.

Edge cases: total must be even. Total 0 is handled correctly because another zero-sum subtree is required after removing the root sum.

Complexity: O(n) time and O(n) space for the stored sums and recursion stack.
"""
