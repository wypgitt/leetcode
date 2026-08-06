#
# @lc app=leetcode id=1973 lang=python3
#
# [1973] Count Nodes Equal to Sum of Descendants
#
# https://leetcode.com/problems/count-nodes-equal-to-sum-of-descendants/description/
#
# algorithms
# Medium (77.31%)
# Likes:    184
# Dislikes: 10
# Total Accepted:    16K
# Total Submissions: 20.7K
# Testcase Example:  "[10,3,4,2,1]"
#
#
# Given the root of a binary tree, return the number of nodes where the
# value of the node is equal to the sum of the values of its descendants.
#
# A descendant of a node x is any node that is on the path from node x to
# some leaf node. The sum is considered to be 0 if the node has no
# descendants.
#
# Example 1:
#
# Input: root = [10,3,4,2,1]
# Output: 2
# Explanation:
# For the node with value 10: The sum of its descendants is 3+4+2+1 = 10.
# For the node with value 3: The sum of its descendants is 2+1 = 3.
#
# Example 2:
#
# Input: root = [2,3,null,2,null]
# Output: 0
# Explanation:
# No node has a value that is equal to the sum of its descendants.
#
# Example 3:
#
# Input: root = [0]
# Output: 1
# For the node with value 0: The sum of its descendants is 0 since it has
# no descendants.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 0 <= Node.val <= 10^5
#
# @lc code=start
from typing import Optional

# Definition for a binary tree node.
try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def equalToDescendants(self, root: Optional["TreeNode"]) -> int:
        """
        Interview explanation:
        Premium. Count nodes whose value equals the sum of all descendants.

        Algorithm:
        - dfs returns subtree sum; if node.val == left_sum+right_sum, count++.
        - Empty child contributes 0; leaf compares to 0.

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional["TreeNode"]) -> int:
            if not node:
                return 0
            left = dfs(node.left)
            right = dfs(node.right)
            if node.val == left + right:
                self.ans += 1
            return node.val + left + right

        dfs(root)
        return self.ans

    def equalToDescendants_stack(self, root: Optional["TreeNode"]) -> int:
        """
        Interview explanation:
        Alternate iterative postorder with explicit stack storing subtree sums.

        Algorithm:
        - Postorder traverse; map node→subtree sum; count equalities.

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return 0
        ans = 0
        sub = {}
        st = [(root, False)]
        while st:
            node, seen = st.pop()
            if seen:
                left = sub.get(node.left, 0)
                right = sub.get(node.right, 0)
                if node.val == left + right:
                    ans += 1
                sub[node] = node.val + left + right
            else:
                st.append((node, True))
                if node.right:
                    st.append((node.right, False))
                if node.left:
                    st.append((node.left, False))
        return ans
# @lc code=end

