#
# @lc app=leetcode id=437 lang=python3
#
# [437] Path Sum III
#
# https://leetcode.com/problems/path-sum-iii/description/
#
# algorithms
# Medium (46.57%)
# Likes:    12020
# Dislikes: 575
# Total Accepted:    820K
# Total Submissions: 1.8M
# Testcase Example:  "[10,5,-3,3,2,null,11,3,-2,null,1]"
#
# Given the root of a binary tree and an integer targetSum, return the number
# of paths where the sum of the values along the path equals targetSum.
#
# The path does not need to start or end at the root or a leaf, but it must go
# downwards (i.e., traveling only from parent nodes to child nodes).
#
# Example 1:
#
# Input: root = [10,5,-3,3,2,null,11,3,-2,null,1], targetSum = 8
# Output: 3
# Explanation: The paths that sum to 8 are shown.
#
# Example 2:
#
# Input: root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
# Output: 3
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 1000].
#
# -10^9 <= Node.val <= 10^9
#
# -1000 <= targetSum <= 1000
#

# @lc code=start

from collections import defaultdict
from typing import Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        """
        Interview explanation:
        Prefix-sum DFS: running sum from root; a path ending at current node
        equals target iff some ancestor prefix equals curr - targetSum.
        HashMap counts of prefix sums along the current path (backtrack).

        Algorithm:
        - dfs(node, curr): ans += count[curr-target]; count[curr]++; recurse;
          count[curr]--.
        - Seed count[0]=1.

        Complexity: O(n) time, O(n) space.
        """
        count = defaultdict(int)
        count[0] = 1
        ans = 0

        def dfs(node: Optional[TreeNode], curr: int) -> None:
            nonlocal ans
            if not node:
                return
            curr += node.val
            ans += count[curr - targetSum]
            count[curr] += 1
            dfs(node.left, curr)
            dfs(node.right, curr)
            count[curr] -= 1

        dfs(root, 0)
        return ans

    def pathSumBrute(self, root: Optional[TreeNode], targetSum: int) -> int:
        """
        Interview explanation:
        Alternate: for each node as path start, DFS downward summing (O(n^2)).

        Algorithm:
        - dfs_from(node, remain) counts paths from this start; outer dfs visits starts.

        Complexity: O(n^2) time, O(h) space.
        """
        def dfs_from(node: Optional[TreeNode], remain: int) -> int:
            if not node:
                return 0
            remain -= node.val
            return (1 if remain == 0 else 0) + dfs_from(node.left, remain) + dfs_from(node.right, remain)

        def dfs(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            return dfs_from(node, targetSum) + dfs(node.left) + dfs(node.right)

        return dfs(root)
# @lc code=end
