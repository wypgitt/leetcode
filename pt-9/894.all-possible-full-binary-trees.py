#
# @lc app=leetcode id=894 lang=python3
#
# [894] All Possible Full Binary Trees
#
# https://leetcode.com/problems/all-possible-full-binary-trees/description/
#
# algorithms
# Medium (82.76%)
# Likes:    5273
# Dislikes: 369
# Total Accepted:    218K
# Total Submissions: 264K
# Testcase Example:  "7"
#
# Given an integer n, return a list of all possible full binary trees with n
# nodes. Each node of each tree in the answer must have Node.val == 0.
#
# Each element of the answer is the root node of one possible tree. You may
# return the final list of trees in any order.
#
# A full binary tree is a binary tree where each node has exactly 0 or 2
# children.
#
# Example 1:
#
# Input: n = 7
# Output:
# [[0,0,0,null,null,0,0,null,null,0,0],[0,0,0,null,null,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,null,null,null,null,0,0],[0,0,0,0,0,null,null,0,0]]
#
# Example 2:
#
# Input: n = 3
# Output: [[0,0,0]]
#
# Constraints:
#
# 1 <= n <= 20
#

# @lc code=start
from functools import lru_cache
from typing import List, Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def allPossibleFBT(self, n: int) -> List[Optional[TreeNode]]:
        """
        Interview explanation:
        Full BT: every node 0 or 2 children. Odd n only. DP/memo: for left
        size i (odd), right = n-1-i; cartesian product of FBT(i) x FBT(right).

        Algorithm (DP/memo):
        - If n even return []. n==1: [TreeNode()].
        - Memo allPossibleFBT(n); combine left/right sizes.

        Complexity: O(Catalan-related) trees; O(2^{n/2}) roughly, memoized.
        """
        return list(self._build(n))

    @lru_cache(None)
    def _build(self, n: int) -> tuple:
        if n % 2 == 0:
            return ()
        if n == 1:
            return (TreeNode(0),)
        res = []
        for left_n in range(1, n, 2):
            right_n = n - 1 - left_n
            for L in self._build(left_n):
                for R in self._build(right_n):
                    res.append(TreeNode(0, L, R))
        return tuple(res)

    def allPossibleFBT_bottom_up(self, n: int) -> List[Optional[TreeNode]]:
        """
        Interview explanation:
        Alternate bottom-up DP: dp[i] = all FBT with i nodes; build increasing i.

        Algorithm:
        - dp[1]=[TreeNode()]; for i odd: for left odd < i: combine dp[left]*dp[i-1-left].

        Complexity: same combinatorial size; O(n) states.
        """
        if n % 2 == 0:
            return []
        dp: List[List[Optional[TreeNode]]] = [[] for _ in range(n + 1)]
        dp[1] = [TreeNode(0)]
        for nodes in range(3, n + 1, 2):
            for left_n in range(1, nodes, 2):
                right_n = nodes - 1 - left_n
                for L in dp[left_n]:
                    for R in dp[right_n]:
                        dp[nodes].append(TreeNode(0, L, R))
        return dp[n]
# @lc code=end

