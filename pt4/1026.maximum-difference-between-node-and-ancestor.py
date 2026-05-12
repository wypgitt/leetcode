#
# @lc app=leetcode id=1026 lang=python3
#
# [1026] Maximum Difference Between Node and Ancestor
#
# https://leetcode.com/problems/maximum-difference-between-node-and-ancestor/description/
#
# algorithms
# Medium (78.15%)
# Likes:    5107
# Dislikes: 171
# Total Accepted:    385.3K
# Total Submissions: 492.9K
# Testcase Example:  '[8,3,10,1,6,null,14,null,null,4,7,13]'
#
# Given the root of a binary tree, find the maximum value v for which there
# exist different nodes a and b where v = |a.val - b.val| and a is an ancestor
# of b.
# 
# A node a is an ancestor of b if either: any child of a is equal to b or any
# child of a is an ancestor of b.
# 
# 
# Example 1:
# 
# 
# Input: root = [8,3,10,1,6,null,14,null,null,4,7,13]
# Output: 7
# Explanation: We have various ancestor-node differences, some of which are
# given below :
# |8 - 3| = 5
# |3 - 7| = 4
# |8 - 1| = 7
# |10 - 13| = 3
# Among all possible differences, the maximum value of 7 is obtained by |8 - 1|
# = 7.
# 
# Example 2:
# 
# 
# Input: root = [1,null,2,null,0,3]
# Output: 3
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [2, 5000].
# 0 <= Node.val <= 10^5
# 
# 
#

# @lc code=start
from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxAncestorDiff(self, root: Optional[TreeNode]) -> int:
        def dfs(node: Optional[TreeNode], path_min: int, path_max: int) -> int:
            if not node:
                return path_max - path_min

            path_min = min(path_min, node.val)
            path_max = max(path_max, node.val)

            return max(
                dfs(node.left, path_min, path_max),
                dfs(node.right, path_min, path_max),
            )

        return dfs(root, root.val, root.val)
# @lc code=end

"""
Interview Explanation

Core idea:
For a node, the largest difference with any ancestor only depends on the
minimum and maximum values seen on the path from the root to that node. We do
not need to compare against every ancestor individually.

Algorithm:
Run DFS from the root while carrying two values:
- path_min: smallest value among ancestors and the current path.
- path_max: largest value among ancestors and the current path.
When a path ends, path_max - path_min is the best difference on that root-to-leaf
path. The answer is the maximum over all paths.

Data structure choice:
The recursion stack naturally represents the current ancestor path. No extra
set or parent map is needed because only the path's min and max matter.

Correctness:
Every ancestor-descendant pair lies on some root-to-node path. For that path,
the maximum absolute difference between two values is exactly max - min. DFS
evaluates max - min for every root-to-leaf path after updating with all nodes
on that path, so it considers the best possible ancestor-descendant difference.

Complexity:
Each node is processed once, so time is O(n). Recursion depth is O(h), where h
is the tree height.

Tests and edge cases:
- A skewed tree works because the running min and max update along the chain.
- Values increasing or decreasing monotonically produce end-to-root difference.
- Equal values are not allowed by the problem? Even if present, difference 0
  is handled naturally.
- The root has no ancestor, but initializing min and max to root.val avoids a
  fake comparison.
"""
