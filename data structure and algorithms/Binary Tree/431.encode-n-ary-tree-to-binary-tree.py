#
# @lc app=leetcode id=431 lang=python3
#
# [431] Encode N-ary Tree to Binary Tree
#
# https://leetcode.com/problems/encode-n-ary-tree-to-binary-tree/description/
#
# algorithms
# Hard (80.67%)
# Likes:    538
# Dislikes: 30
# Total Accepted:    25.3K
# Total Submissions: 31.4K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
#
# Design an algorithm to encode an N-ary tree into a binary tree and
# decode the binary tree to get the original N-ary tree. An N-ary tree is
# a rooted tree in which each node has no more than N children. Similarly,
# a binary tree is a rooted tree in which each node has no more than 2
# children. There is no restriction on how your encode/decode algorithm
# should work. You just need to ensure that an N-ary tree can be encoded
# to a binary tree and this binary tree can be decoded to the original
# N-nary tree structure.
#
# Nary-Tree input serialization is represented in their level order
# traversal, each group of children is separated by the null value (See
# following example).
#
# For example, you may encode the following 3-ary tree to a binary tree in
# this way:
#
# Input: root = [1,null,3,2,4,null,5,6]
#
# Note that the above is just an example which might or might not work.
# You do not necessarily need to follow this format, so please be creative
# and come up with different approaches yourself.
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: [1,null,3,2,4,null,5,6]
#
# Example 2:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output:
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
#
# Example 3:
#
# Input: root = []
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# 0 <= Node.val <= 10^4
#
# The height of the n-ary tree is less than or equal to 1000
#
# Do not use class member/global/static variables to store states. Your
# encode and decode algorithms should be stateless.
#
# @lc code=start

from typing import List, Optional


# Definition for a Node (N-ary).
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List["Node"]] = None):
        self.val = val
        self.children = children if children is not None else []


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x: int):
        self.val = x
        self.left = None
        self.right = None


class Codec:
    def encode(self, root: "Optional[Node]") -> "Optional[TreeNode]":
        """
        Interview explanation:
        Left-child right-sibling encoding: binary left points to the first
        N-ary child; binary right points to the next sibling.

        Algorithm:
        - If no root: None. Create TreeNode(val).
        - Encode children left-to-right as a right-linked sibling chain;
          attach first child as left.

        Complexity: O(n) time and space.
        """
        if not root:
            return None
        b = TreeNode(root.val)
        if not root.children:
            return b
        b.left = self.encode(root.children[0])
        cur = b.left
        for ch in root.children[1:]:
            cur.right = self.encode(ch)
            cur = cur.right
        return b

    def decode(self, data: "Optional[TreeNode]") -> "Optional[Node]":
        """
        Interview explanation:
        Inverse of left-child right-sibling: binary left is first child; walk
        the right chain to collect siblings as N-ary children.

        Algorithm:
        - Create Node(val); walk data.left then .right siblings; decode each.

        Complexity: O(n) time and space.
        """
        if not data:
            return None
        root = Node(data.val, [])
        cur = data.left
        while cur:
            root.children.append(self.decode(cur))
            cur = cur.right
        return root


# Your Codec object will be instantiated and called as such:
# codec = Codec()
# codec.decode(codec.encode(root))
# @lc code=end
