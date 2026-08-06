#
# @lc app=leetcode id=2583 lang=python3
#
# [2583] Kth Largest Sum in a Binary Tree
#
# https://leetcode.com/problems/kth-largest-sum-in-a-binary-tree/description/
#
# algorithms
# Medium (58.97%)
# Likes:    1102
# Dislikes: 40
# Total Accepted:    187.1K
# Total Submissions: 317.3K
# Testcase Example:  "[5,8,9,2,1,3,7,4,6]\n2"
#
# You are given the root of a binary tree and a positive integer k.
#
# The level sum in the tree is the sum of the values of the nodes that are on
# the same level.
#
# Return the k^th largest level sum in the tree (not necessarily distinct). If
# there are fewer than k levels in the tree, return -1.
#
# Note that two nodes are on the same level if they have the same distance from
# the root.
#
#
#
# Example 1:
#
# Input: root = [5,8,9,2,1,3,7,4,6], k = 2
# Output: 13
# Explanation: The level sums are the following:
# - Level 1: 5.
# - Level 2: 8 + 9 = 17.
# - Level 3: 2 + 1 + 3 + 7 = 13.
# - Level 4: 4 + 6 = 10.
# The 2^nd largest level sum is 13.
#
# Example 2:
#
# Input: root = [1,2,null,3], k = 1
# Output: 3
# Explanation: The largest level sum is 3.
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
# 1 <= Node.val <= 10^6
#
#
# 1 <= k <= n
#

# @lc code=start
from typing import Optional, List
from collections import deque
import heapq

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def kthLargestLevelSum(self, root: Optional['TreeNode'], k: int) -> int:
        """
        Interview explanation:
        Compute sum of node values per level; return the k-th largest level sum (or -1).

        Algorithm:
        - BFS by levels accumulate sums; sort descending (or maintain a heap of size k).

        Complexity: O(n + h log h) time, O(w) space.
        """
        if not root:
            return -1
        q = deque([root])
        sums = []
        while q:
            s = 0
            for _ in range(len(q)):
                node = q.popleft()
                s += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            sums.append(s)
        if k > len(sums):
            return -1
        sums.sort(reverse=True)
        return sums[k - 1]

    def kthLargestLevelSum_bfs(self, root: Optional['TreeNode'], k: int) -> int:
        """
        Interview explanation:
        BFS level sums with a min-heap of size k for the k-th largest.

        Algorithm:
        - Level-order; push each level sum into a size-k heap.

        Complexity: O(n + h log k) time, O(w+k) space.
        """
        if not root:
            return -1
        q = deque([root])
        heap = []
        while q:
            s = 0
            for _ in range(len(q)):
                node = q.popleft()
                s += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            heapq.heappush(heap, s)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0] if len(heap) == k else -1
# @lc code=end
