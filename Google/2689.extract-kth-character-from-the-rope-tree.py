#
# @lc app=leetcode id=2689 lang=python3
#
# [2689] Extract Kth Character From The Rope Tree
#
# https://leetcode.com/problems/extract-kth-character-from-the-rope-tree/description/
#
# algorithms
# Easy (73.25%)
# Likes:    42
# Dislikes: 29
# Total Accepted:    5.1K
# Total Submissions: 7K
# Testcase Example:  "[10,4,\"abcpoe\",\"g\",\"rta\"]\n6"
#
#
# You are given the root of a binary tree and an integer k. Besides the
# left and right children, every node of this tree has two other
# properties, a string node.val containing only lowercase English letters
# (possibly empty) and a non-negative integer node.len. There are two
# types of nodes in this tree:
#
# Leaf: These nodes have no children, node.len = 0, and node.val is some
# non-empty string.
#
# Internal: These nodes have at least one child (also at most two
# children), node.len > 0, and node.val is an empty string.
#
# The tree described above is called a Rope binary tree. Now we define
# S[node] recursively as follows:
#
# If node is some leaf node, S[node] = node.val,
#
# Otherwise if node is some internal node, S[node] = concat(S[node.left],
# S[node.right]) and S[node].length = node.len.
#
# Return k-th character of the string S[root].
#
# Note: If s and p are two strings, concat(s, p) is a string obtained by
# concatenating p to s. For example, concat("ab", "zz") = "abzz".
#
# Example 1:
#
# Input: root = [10,4,"abcpoe","g","rta"], k = 6
# Output: "b"
# Explanation: In the picture below, we put an integer on internal nodes
# that represents node.len, and a string on leaf nodes that represents
# node.val.
# You can see that S[root] = concat(concat("g", "rta"), "abcpoe") =
# "grtaabcpoe". So S[root][5], which represents 6th character of it, is
# equal to "b".
#
# Example 2:
#
# Input: root = [12,6,6,"abc","efg","hij","klm"], k = 3
# Output: "c"
# Explanation: In the picture below, we put an integer on internal nodes
# that represents node.len, and a string on leaf nodes that represents
# node.val.
# You can see that S[root] = concat(concat("abc", "efg"), concat("hij",
# "klm")) = "abcefghijklm". So S[root][2], which represents the 3rd
# character of it, is equal to "c".
#
# Example 3:
#
# Input: root = ["ropetree"], k = 8
# Output: "e"
# Explanation: In the picture below, we put an integer on internal nodes
# that represents node.len, and a string on leaf nodes that represents
# node.val.
# You can see that S[root] = "ropetree". So S[root][7], which represents
# 8th character of it, is equal to "e".
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^3]
#
# node.val contains only lowercase English letters
#
# 0 <= node.val.length <= 50
#
# 0 <= node.len <= 10^4
#
# for leaf nodes, node.len = 0 and node.val is non-empty
#
# for internal nodes, node.len > 0 and node.val is empty
#
# 1 <= k <= S[root].length
#
# @lc code=start

from typing import Optional

# Definition for a rope tree node.
# class RopeTreeNode:
#     def __init__(self, len=0, val="", left=None, right=None):
#         self.len = len
#         self.val = val
#         self.left = left
#         self.right = right

try:
    RopeTreeNode  # type: ignore[name-defined]
except NameError:

    class RopeTreeNode:  # type: ignore[no-redef]
        def __init__(self, len=0, val="", left=None, right=None):
            self.len = len
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def getKthCharacter(self, root: Optional[object], k: int) -> str:
        """
        Interview explanation:
        Premium rope tree: leaves hold strings; internal nodes have len = concat length.
        Return the k-th character (1-indexed) of S[root].

        Algorithm:
        - Descend using left subtree length (left.len or len(left.val)); go left if k in left else
          subtract and go right. At leaf return val[k-1].

        Complexity: O(h + L) time for leaf length L, O(1) extra space.
        """
        def length(node: Optional[RopeTreeNode]) -> int:
            if node is None:
                return 0
            if node.len == 0:
                return len(node.val)
            return node.len

        node = root
        while node is not None and node.len > 0:
            left_len = length(node.left)
            if k <= left_len:
                node = node.left
            else:
                k -= left_len
                node = node.right
        return node.val[k - 1]

    def getKthCharacter_build(self, root: Optional[object], k: int) -> str:
        """
        Interview explanation:
        Alternate: fully materialize S[root] then index (fine for small constraints).

        Algorithm:
        - DFS concat leaf strings; return s[k-1].

        Complexity: O(|S|) time and space.
        """
        def dfs(node: Optional[RopeTreeNode]) -> str:
            if node is None:
                return ""
            if node.len == 0:
                return node.val
            return dfs(node.left) + dfs(node.right)

        return dfs(root)[k - 1]
# @lc code=end
