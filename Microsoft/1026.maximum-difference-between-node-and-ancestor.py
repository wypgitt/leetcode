#
# @lc app=leetcode id=1026 lang=python3
#
# [1026] Maximum Difference Between Node and Ancestor
#
# https://leetcode.com/problems/maximum-difference-between-node-and-ancestor/description/
#
# algorithms
# Medium (78.22%)
# Likes:    5121
# Dislikes: 171
# Total Accepted:    391K
# Total Submissions: 500K
# Testcase Example:  "[8,3,10,1,6,null,14,null,null,4,7,13]"
#
# Given the root of a binary tree, find the maximum value v for which there
# exist different nodes a and b where v = |a.val - b.val| and a is an ancestor
# of b.
#
# A node a is an ancestor of b if either: any child of a is equal to b or any
# child of a is an ancestor of b.
#
# Example 1:
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
# Input: root = [1,null,2,null,0,3]
# Output: 3
#
# Constraints:
#
# The number of nodes in the tree is in the range [2, 5000].
#
# 0 <= Node.val <= 10^5
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
        """
        Interview explanation:
        Along any root-to-node path, the max |ancestor-node| equals
        max_on_path - min_on_path at that node. DFS carrying running min/max.

        Algorithm:
        - dfs(node, mn, mx): update ans with max(|val-mn|,|val-mx|); recurse with
          updated mn/mx; return ans

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional[TreeNode], mn: int, mx: int) -> None:
            if not node:
                return
            self.ans = max(self.ans, abs(node.val - mn), abs(node.val - mx))
            mn = min(mn, node.val)
            mx = max(mx, node.val)
            dfs(node.left, mn, mx)
            dfs(node.right, mn, mx)

        dfs(root, root.val, root.val)
        return self.ans

    def maxAncestorDiff_bfs(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Alternate BFS carrying (node, path_min, path_max).

        Algorithm:
        - Queue (node, mn, mx); update ans; enqueue children with updated bounds

        Complexity: O(n) time, O(n) space.
        """
        from collections import deque

        ans = 0
        q = deque([(root, root.val, root.val)])
        while q:
            node, mn, mx = q.popleft()
            ans = max(ans, abs(node.val - mn), abs(node.val - mx))
            mn2, mx2 = min(mn, node.val), max(mx, node.val)
            if node.left:
                q.append((node.left, mn2, mx2))
            if node.right:
                q.append((node.right, mn2, mx2))
        return ans
# @lc code=end
