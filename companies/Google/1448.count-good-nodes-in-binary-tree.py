#
# @lc app=leetcode id=1448 lang=python3
#
# [1448] Count Good Nodes in Binary Tree
#
# https://leetcode.com/problems/count-good-nodes-in-binary-tree/description/
#
# algorithms
# Medium (73.94%)
# Likes:    6424
# Dislikes: 215
# Total Accepted:    923K
# Total Submissions: 1.2M
# Testcase Example:  "[3,1,4,3,null,1,5]"
#
# Given a binary tree root, a node X in the tree is named good if in the path
# from root to X there are no nodes with a value greater than X.
#
# Return the number of good nodes in the binary tree.
#
# Example 1:
#
# Input: root = [3,1,4,3,null,1,5]
# Output: 4
# Explanation: Nodes in blue are good.
# Root Node (3) is always a good node.
# Node 4 -> (3,4) is the maximum value in the path starting from the root.
# Node 5 -> (3,4,5) is the maximum value in the path
# Node 3 -> (3,1,3) is the maximum value in the path.
#
# Example 2:
#
# Input: root = [3,3,null,4,2]
# Output: 3
# Explanation: Node 2 -> (3, 3, 2) is not good, because "3" is higher than it.
#
# Example 3:
#
# Input: root = [1]
# Output: 1
# Explanation: Root is considered as good.
#
# Constraints:
#
# The number of nodes in the binary tree is in the range [1, 10^5].
#
# Each node's value is between [-10^4, 10^4].
#

# @lc code=start
from typing import Optional
from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def goodNodes(self, root: TreeNode) -> int:
        """
        Interview explanation:
        A node is good if on the path from root no larger value appears.
        DFS carrying the max so far; count when node.val >= max_so_far.

        Algorithm:
        (DFS)
        - dfs(node, mx): ans += node.val>=mx; recurse with max(mx,node.val)

        Complexity: O(n) time, O(h) space.
        """
        def dfs(node: Optional[TreeNode], mx: int) -> int:
            if not node:
                return 0
            good = 1 if node.val >= mx else 0
            nmx = max(mx, node.val)
            return good + dfs(node.left, nmx) + dfs(node.right, nmx)

        return dfs(root, root.val if root else 0)

    def goodNodes_bfs(self, root: TreeNode) -> int:
        """
        Interview explanation:
        Alternate BFS queue of (node, max_on_path).

        Algorithm:
        - BFS; count goods; push children with updated max.

        Complexity: O(n) time, O(w) space.
        """
        if not root:
            return 0
        ans = 0
        q = deque([(root, root.val)])
        while q:
            node, mx = q.popleft()
            if node.val >= mx:
                ans += 1
            nmx = max(mx, node.val)
            if node.left:
                q.append((node.left, nmx))
            if node.right:
                q.append((node.right, nmx))
        return ans
# @lc code=end
