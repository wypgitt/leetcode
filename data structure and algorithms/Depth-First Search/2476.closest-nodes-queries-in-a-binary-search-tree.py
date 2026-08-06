#
# @lc app=leetcode id=2476 lang=python3
#
# [2476] Closest Nodes Queries in a Binary Search Tree
#
# https://leetcode.com/problems/closest-nodes-queries-in-a-binary-search-tree/description/
#
# algorithms
# Medium (44.82%)
# Likes:    546
# Dislikes: 145
# Total Accepted:    41.3K
# Total Submissions: 92.2K
# Testcase Example:  "[6,2,13,1,4,9,15,null,null,null,null,null,null,14]\n[2,5,16]"
#
# You are given the root of a binary search tree and an array queries of size n
# consisting of positive integers.
#
# Find a 2D array answer of size n where answer[i] = [min_i, max_i]:
#
#
# min_i is the largest value in the tree that is smaller than or equal to
# queries[i]. If a such value does not exist, add -1 instead.
#
#
# max_i is the smallest value in the tree that is greater than or equal to
# queries[i]. If a such value does not exist, add -1 instead.
#
# Return the array answer.
#
#
#
# Example 1:
#
# Input: root = [6,2,13,1,4,9,15,null,null,null,null,null,null,14], queries =
# [2,5,16]
# Output: [[2,2],[4,6],[15,-1]]
# Explanation: We answer the queries in the following way:
# - The largest number that is smaller or equal than 2 in the tree is 2, and the
# smallest number that is greater or equal than 2 is still 2. So the answer for
# the first query is [2,2].
# - The largest number that is smaller or equal than 5 in the tree is 4, and the
# smallest number that is greater or equal than 5 is 6. So the answer for the
# second query is [4,6].
# - The largest number that is smaller or equal than 16 in the tree is 15, and
# the smallest number that is greater or equal than 16 does not exist. So the
# answer for the third query is [15,-1].
#
# Example 2:
#
# Input: root = [4,null,9], queries = [3]
# Output: [[-1,4]]
# Explanation: The largest number that is smaller or equal to 3 in the tree does
# not exist, and the smallest number that is greater or equal to 3 is 4. So the
# answer for the query is [-1,4].
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is in the range [2, 10^5].
#
#
# 1 <= Node.val <= 10^6
#
#
# n == queries.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= queries[i] <= 10^6
#

# @lc code=start
from typing import List, Optional
from bisect import bisect_left


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def closestNodes(
        self, root: Optional["TreeNode"], queries: List[int]
    ) -> List[List[int]]:
        """
        Interview explanation:
        BST queries: for each query return [largest <= q, smallest >= q]
        (-1 if missing).

        Algorithm:
        - Inorder flatten to sorted array; binary search each query.

        Complexity: O(n + q log n) time, O(n) space.
        """
        arr = []

        def inorder(node) -> None:
            if not node:
                return
            inorder(node.left)
            arr.append(node.val)
            inorder(node.right)

        inorder(root)
        ans = []
        for q in queries:
            i = bisect_left(arr, q)
            mn = arr[i] if i < len(arr) else -1
            if i < len(arr) and arr[i] == q:
                mx = q
            else:
                mx = arr[i - 1] if i > 0 else -1
            ans.append([mx, mn])
        return ans

    def closestNodes_bst(
        self, root: Optional["TreeNode"], queries: List[int]
    ) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: answer each query by walking the BST (no flatten).

        Algorithm:
        - Track floor/ceil while comparing query to node values.

        Complexity: O(q * h) time, O(1) extra space.
        """
        def query(node, q: int):
            floor = ceil = -1
            while node:
                if node.val == q:
                    return [q, q]
                if node.val < q:
                    floor = node.val
                    node = node.right
                else:
                    ceil = node.val
                    node = node.left
            return [floor, ceil]

        return [query(root, q) for q in queries]
# @lc code=end

