#
# @lc app=leetcode id=1261 lang=python3
#
# [1261] Find Elements in a Contaminated Binary Tree
#
# https://leetcode.com/problems/find-elements-in-a-contaminated-binary-tree/description/
#
# algorithms
# Medium (84.10%)
# Likes:    1434
# Dislikes: 127
# Total Accepted:    204.5K
# Total Submissions: 243.2K
# Testcase Example:  '["FindElements","find","find"]\n[[[-1,null,-1]],[1],[2]]'
#
# Given a binary tree with the following rules:
# 
# 
# root.val == 0
# For any treeNode:
# 
# If treeNode.val has a value x and treeNode.left != null, then
# treeNode.left.val == 2 * x + 1
# If treeNode.val has a value x and treeNode.right != null, then
# treeNode.right.val == 2 * x + 2
# 
# 
# 
# 
# Now the binary tree is contaminated, which means all treeNode.val have been
# changed to -1.
# 
# Implement the FindElements class:
# 
# 
# FindElements(TreeNode* root) Initializes the object with a contaminated
# binary tree and recovers it.
# bool find(int target) Returns true if the target value exists in the
# recovered binary tree.
# 
# 
# 
# Example 1:
# 
# 
# Input
# ["FindElements","find","find"]
# [[[-1,null,-1]],[1],[2]]
# Output
# [null,false,true]
# Explanation
# FindElements findElements = new FindElements([-1,null,-1]); 
# findElements.find(1); // return False 
# findElements.find(2); // return True 
# 
# Example 2:
# 
# 
# Input
# ["FindElements","find","find","find"]
# [[[-1,-1,-1,-1,-1]],[1],[3],[5]]
# Output
# [null,true,true,false]
# Explanation
# FindElements findElements = new FindElements([-1,-1,-1,-1,-1]);
# findElements.find(1); // return True
# findElements.find(3); // return True
# findElements.find(5); // return False
# 
# Example 3:
# 
# 
# Input
# ["FindElements","find","find","find","find"]
# [[[-1,null,-1,-1,null,-1]],[2],[3],[4],[5]]
# Output
# [null,true,false,false,true]
# Explanation
# FindElements findElements = new FindElements([-1,null,-1,-1,null,-1]);
# findElements.find(2); // return True
# findElements.find(3); // return False
# findElements.find(4); // return False
# findElements.find(5); // return True
# 
# 
# 
# Constraints:
# 
# 
# TreeNode.val == -1
# The height of the binary tree is less than or equal to 20
# The total number of nodes is between [1, 10^4]
# Total calls of find() is between [1, 10^4]
# 0 <= target <= 10^6
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class FindElements:

    def __init__(self, root: Optional[TreeNode]):
        self.values = set()

        def recover(node, value: int) -> None:
            if not node:
                return
            node.val = value
            self.values.add(value)
            recover(node.left, 2 * value + 1)
            recover(node.right, 2 * value + 2)

        recover(root, 0)

    def find(self, target: int) -> bool:
        return target in self.values


# Your FindElements object will be instantiated and called as such:
# obj = FindElements(root)
# param_1 = obj.find(target)
# @lc code=end

# Explanation
# -----------
# The recovery rules are deterministic: root is 0, left child is 2*x + 1, and
# right child is 2*x + 2. DFS the contaminated tree once, assign each recovered
# value, and store it in a set.
#
# The set makes find(target) O(1)-average, which is the point of doing the
# recovery work in the constructor instead of walking the tree on every query.
#
# Edge cases: missing children are skipped; target can be much larger than any
# recovered value; the root alone recovers to {0}.
#
# Time complexity: constructor O(n), find O(1) average.
# Space complexity: O(n) for recovered values plus recursion stack.
