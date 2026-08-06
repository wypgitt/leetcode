#
# @lc app=leetcode id=1602 lang=python3
#
# [1602] Find Nearest Right Node in Binary Tree
#
# https://leetcode.com/problems/find-nearest-right-node-in-binary-tree/description/
#
# algorithms
# Medium (75.10%)
# Likes:    333
# Dislikes: 10
# Total Accepted:    25.2K
# Total Submissions: 33.6K
# Testcase Example:  "[1,2,3,null,4,5,6]\n4"
#
#
# Given the root of a binary tree and a node u in the tree, return the
# nearest node on the same level that is to the right of u, or return null
# if u is the rightmost node in its level.
#
# Example 1:
#
# Input: root = [1,2,3,null,4,5,6], u = 4
# Output: 5
# Explanation: The nearest node on the same level to the right of node 4
# is node 5.
#
# Example 2:
#
# Input: root = [3,null,4,2], u = 2
# Output: null
# Explanation: There are no nodes to the right of 2.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 1 <= Node.val <= 10^5
#
# All values in the tree are distinct.
#
# u is a node in the binary tree rooted at root.
#
# @lc code=start
from typing import Optional
from collections import deque

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def findNearestRightNode(self, root: TreeNode, u: TreeNode) -> Optional[TreeNode]:
        """
        Interview explanation:
        Premium. Nearest right node = next node to the right on the same BFS level
        as u (or None). Level-order BFS is the natural fit.

        Algorithm (BFS):
        - Queue level by level; when u is found, return the next node in that level
          if any; else None after finishing the level.

        Complexity: O(n) time, O(w) space.
        """
        q = deque([root])
        while q:
            sz = len(q)
            for i in range(sz):
                node = q.popleft()
                if node is u:
                    return q[0] if i + 1 < sz else None
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
        return None

    def findNearestRightNode_dfs(self, root: TreeNode, u: TreeNode) -> Optional[TreeNode]:
        """
        Interview explanation:
        Alternate DFS: record depth of u, then find first node at that depth with
        larger inorder/preorder position (or second pass tracking prev on level).

        Algorithm (DFS two-phase):
        - First DFS find depth of u. Second DFS inorder left-to-right by depth;
          after seeing u at that depth, next node at same depth is answer.

        Complexity: O(n) time, O(h) space.
        """
        target_depth = -1
        found_u = False
        ans = None

        def dfs(node: Optional[TreeNode], d: int) -> None:
            nonlocal target_depth, found_u, ans
            if not node or ans is not None:
                return
            if node is u:
                target_depth = d
                found_u = True
                dfs(node.left, d + 1)
                dfs(node.right, d + 1)
                return
            if found_u and d == target_depth:
                ans = node
                return
            dfs(node.left, d + 1)
            dfs(node.right, d + 1)

        dfs(root, 0)
        return ans
# @lc code=end
