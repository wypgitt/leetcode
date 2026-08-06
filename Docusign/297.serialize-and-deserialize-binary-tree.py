#
# @lc app=leetcode id=297 lang=python3
#
# [297] Serialize and Deserialize Binary Tree
#
# https://leetcode.com/problems/serialize-and-deserialize-binary-tree/description/
#
# algorithms
# Hard (61.13%)
# Likes:    11282
# Dislikes: 437
# Total Accepted:    1.2M
# Total Submissions: 2.0M
# Testcase Example:  "[1,2,3,null,null,4,5]"
#
# Serialization is the process of converting a data structure or object into a
# sequence of bits so that it can be stored in a file or memory buffer, or
# transmitted across a network connection link to be reconstructed later in the
# same or another computer environment.
#
# Design an algorithm to serialize and deserialize a binary tree. There is no
# restriction on how your serialization/deserialization algorithm should work.
# You just need to ensure that a binary tree can be serialized to a string and
# this string can be deserialized to the original tree structure.
#
# Clarification: The input/output format is the same as how LeetCode serializes
# a binary tree. You do not necessarily need to follow this format, so please
# be creative and come up with different approaches yourself.
#
# Example 1:
#
# Input: root = [1,2,3,null,null,4,5]
# Output: [1,2,3,null,null,4,5]
#
# Example 2:
#
# Input: root = []
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# -1000 <= Node.val <= 1000
#

# @lc code=start
from collections import deque

# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None


class Codec:
    def serialize(self, root):
        """
        Interview explanation:
        Level-order BFS serialization with null markers so structure is unique.
        Join values with commas; nulls as '#'.

        Algorithm:
        - BFS queue; for each node append val or '#'; enqueue children only if non-null.
        - Join parts with ','.

        Complexity: O(n) time and space.
        """
        if not root:
            return ""
        q = deque([root])
        parts = []
        while q:
            node = q.popleft()
            if node:
                parts.append(str(node.val))
                q.append(node.left)
                q.append(node.right)
            else:
                parts.append("#")
        return ",".join(parts)

    def deserialize(self, data):
        """
        Interview explanation:
        Rebuild the tree from the BFS string: create root, then assign left/right
        children from the token stream in the same level order.

        Algorithm:
        - Split on ','; queue of parents; consume two tokens per parent for L/R.
        - '#' means null; otherwise create TreeNode and enqueue it.

        Complexity: O(n) time and space.
        """
        if not data:
            return None
        parts = data.split(",")
        root = TreeNode(int(parts[0]))
        q = deque([root])
        i = 1
        while q and i < len(parts):
            node = q.popleft()
            if parts[i] != "#":
                node.left = TreeNode(int(parts[i]))
                q.append(node.left)
            i += 1
            if i < len(parts) and parts[i] != "#":
                node.right = TreeNode(int(parts[i]))
                q.append(node.right)
            i += 1
        return root


class CodecDFS:
    """
    Interview explanation:
    Alternate: preorder DFS with null markers. Serialize visits root-left-right
    writing '#' for nulls; deserialize consumes tokens with the same recursion.
    """

    def serialize(self, root):
        """
        Interview explanation:
        Preorder walk: emit value then left then right; emit '#' for nulls so
        structure is unambiguous.

        Algorithm:
        - DFS append str(val) or '#'; recurse left/right; join with ','.

        Complexity: O(n) time and space.
        """
        parts = []

        def dfs(node):
            if not node:
                parts.append("#")
                return
            parts.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ",".join(parts)

    def deserialize(self, data):
        """
        Interview explanation:
        Mirror preorder serialization: consume next token; '#' → None, else
        build node and recurse for left then right.

        Algorithm:
        - Iterator over split tokens; recursive dfs() builds each subtree.

        Complexity: O(n) time and space.
        """
        parts = iter(data.split(","))

        def dfs():
            val = next(parts)
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node

        return dfs()


# Your Codec object will be instantiated and called as such:
# ser = Codec()
# deser = Codec()
# ans = deser.deserialize(ser.serialize(root))
# @lc code=end

