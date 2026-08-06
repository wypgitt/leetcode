#
# @lc app=leetcode id=1902 lang=python3
#
# [1902] Depth of BST Given Insertion Order
#
# https://leetcode.com/problems/depth-of-bst-given-insertion-order/description/
#
# algorithms
# Medium (42.76%)
# Likes:    111
# Dislikes: 12
# Total Accepted:    3.1K
# Total Submissions: 7.2K
# Testcase Example:  "[2,1,4,3]"
#
#
# You are given a 0-indexed integer array order of length n, a permutation
# of integers from 1 to n representing the order of insertion into a
# binary search tree.
#
# A binary search tree is defined as follows:
#
# The left subtree of a node contains only nodes with keys less than the
# node's key.
#
# The right subtree of a node contains only nodes with keys greater than
# the node's key.
#
# Both the left and right subtrees must also be binary search trees.
#
# The binary search tree is constructed as follows:
#
# order[0] will be the root of the binary search tree.
#
# All subsequent elements are inserted as the child of any existing node
# such that the binary search tree properties hold.
#
# Return the depth of the binary search tree.
#
# A binary tree's depth is the number of nodes along the longest path from
# the root node down to the farthest leaf node.
#
# Example 1:
#
# Input: order = [2,1,4,3]
# Output: 3
# Explanation: The binary search tree has a depth of 3 with path 2->3->4.
#
# Example 2:
#
# Input: order = [2,1,3,4]
# Output: 3
# Explanation: The binary search tree has a depth of 3 with path 2->3->4.
#
# Example 3:
#
# Input: order = [1,2,3,4]
# Output: 4
# Explanation: The binary search tree has a depth of 4 with path
# 1->2->3->4.
#
# Constraints:
#
# n == order.length
#
# 1 <= n <= 10^5
#
# order is a permutation of integers between 1 and n.
#
# @lc code=start
from typing import List, Optional


class Solution:
    def maxDepthBST(self, order: List[int]) -> int:
        """
        Interview explanation:
        Premium. Insert values in given order into a BST; return max depth.
        Maintain an ordered map value→depth. New value's depth is 1 + max of
        predecessor/successor depths among already inserted values.

        Algorithm:
        - Treap/BST ordered by value stores depths; insert x, query pred/succ.

        Complexity: O(n log n) expected time, O(n) space.
        """
        import random

        class Node:
            __slots__ = ("key", "depth", "prio", "left", "right")

            def __init__(self, key, depth):
                self.key = key
                self.depth = depth
                self.prio = random.randrange(1 << 30)
                self.left = None
                self.right = None

        def split(root, key):
            if not root:
                return None, None
            if root.key < key:
                a, b = split(root.right, key)
                root.right = a
                return root, b
            a, b = split(root.left, key)
            root.left = b
            return a, root

        def merge(a, b):
            if not a or not b:
                return a or b
            if a.prio < b.prio:
                a.right = merge(a.right, b)
                return a
            b.left = merge(a, b.left)
            return b

        def max_node(root):
            while root and root.right:
                root = root.right
            return root

        def min_node(root):
            while root and root.left:
                root = root.left
            return root

        root = None
        ans = 0
        for x in order:
            L, R = split(root, x)
            pred = max_node(L)
            succ = min_node(R)
            d = 1
            if pred:
                d = max(d, pred.depth + 1)
            if succ:
                d = max(d, succ.depth + 1)
            root = merge(merge(L, Node(x, d)), R)
            ans = max(ans, d)
        return ans

    def maxDepthBST_simulate(self, order: List[int]) -> int:
        """
        Interview explanation:
        Alternate: literally insert into a pointer BST (O(n^2) skewed worst-case).

        Algorithm:
        - Root=first; walk/insert each next value; track depth.

        Complexity: O(n^2) worst time, O(n) space.
        """
        if not order:
            return 0

        class TNode:
            __slots__ = ("v", "l", "r")

            def __init__(self, v):
                self.v = v
                self.l = self.r = None

        root = TNode(order[0])
        ans = 1
        for x in order[1:]:
            cur, d = root, 1
            while True:
                d += 1
                if x < cur.v:
                    if cur.l is None:
                        cur.l = TNode(x)
                        ans = max(ans, d)
                        break
                    cur = cur.l
                else:
                    if cur.r is None:
                        cur.r = TNode(x)
                        ans = max(ans, d)
                        break
                    cur = cur.r
        return ans
# @lc code=end
