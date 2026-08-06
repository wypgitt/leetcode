#
# @lc app=leetcode id=2458 lang=python3
#
# [2458] Height of Binary Tree After Subtree Removal Queries
#
# https://leetcode.com/problems/height-of-binary-tree-after-subtree-removal-queries/description/
#
# algorithms
# Hard (54.92%)
# Likes:    1565
# Dislikes: 38
# Total Accepted:    106.5K
# Total Submissions: 193.9K
# Testcase Example:  "[1,3,4,2,null,6,5,null,null,null,null,null,7]\n[4]"
#
# You are given the root of a binary tree with n nodes. Each node is assigned a
# unique value from 1 to n. You are also given an array queries of size m.
#
# You have to perform m independent queries on the tree where in the i^th query
# you do the following:
#
#
# Remove the subtree rooted at the node with the value queries[i] from the tree.
# It is guaranteed that queries[i] will not be equal to the value of the root.
#
# Return an array answer of size m where answer[i] is the height of the tree
# after performing the i^th query.
#
# Note:
#
#
# The queries are independent, so the tree returns to its initial state after
# each query.
#
#
# The height of a tree is the number of edges in the longest simple path from
# the root to some node in the tree.
#
#
#
# Example 1:
#
# Input: root = [1,3,4,2,null,6,5,null,null,null,null,null,7], queries = [4]
# Output: [2]
# Explanation: The diagram above shows the tree after removing the subtree
# rooted at node with value 4.
# The height of the tree is 2 (The path 1 -> 3 -> 2).
#
# Example 2:
#
# Input: root = [5,8,9,2,1,3,7,4,6], queries = [3,2,4,8]
# Output: [3,2,3,2]
# Explanation: We have the following queries:
# - Removing the subtree rooted at node with value 3. The height of the tree
# becomes 3 (The path 5 -> 8 -> 2 -> 4).
# - Removing the subtree rooted at node with value 2. The height of the tree
# becomes 2 (The path 5 -> 8 -> 1).
# - Removing the subtree rooted at node with value 4. The height of the tree
# becomes 3 (The path 5 -> 8 -> 2 -> 6).
# - Removing the subtree rooted at node with value 8. The height of the tree
# becomes 2 (The path 5 -> 9 -> 3).
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is n.
#
#
# 2 <= n <= 10^5
#
#
# 1 <= Node.val <= n
#
#
# All the values in the tree are unique.
#
#
# m == queries.length
#
#
# 1 <= m <= min(n, 10^4)
#
#
# 1 <= queries[i] <= n
#
#
# queries[i] != root.val
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
    def treeQueries(self, root: Optional["TreeNode"], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        For each query node, return height of the tree after removing that
        node's entire subtree.

        Algorithm:
        - Precompute subtree heights; DFS carrying the best remaining height
          from ancestors/siblings: depth + 1 + sibling_height.

        Complexity: O(n + q) time, O(n) space.
        """
        height = {}

        def get_h(node) -> int:
            if not node:
                return -1
            h = 1 + max(get_h(node.left), get_h(node.right))
            height[node.val] = h
            return h

        get_h(root)
        ans_map = {}

        def dfs(node, depth: int, best_without: int) -> None:
            if not node:
                return
            ans_map[node.val] = best_without
            lh = height[node.left.val] if node.left else -1
            rh = height[node.right.val] if node.right else -1
            dfs(node.left, depth + 1, max(best_without, depth + 1 + rh))
            dfs(node.right, depth + 1, max(best_without, depth + 1 + lh))

        dfs(root, 0, 0)
        return [ans_map[q] for q in queries]
# @lc code=end

