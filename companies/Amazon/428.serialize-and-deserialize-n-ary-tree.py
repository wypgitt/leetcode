#
# @lc app=leetcode id=428 lang=python3
#
# [428] Serialize and Deserialize N-ary Tree
#
# https://leetcode.com/problems/serialize-and-deserialize-n-ary-tree/description/
#
# algorithms
# Hard (68.92%)
# Likes:    1077
# Dislikes: 58
# Total Accepted:    101.4K
# Total Submissions: 147.2K
# Testcase Example:  "[1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]"
#
#
# Serialization is the process of converting a data structure or object
# into a sequence of bits so that it can be stored in a file or memory
# buffer, or transmitted across a network connection link to be
# reconstructed later in the same or another computer environment.
#
# Design an algorithm to serialize and deserialize an N-ary tree. An N-ary
# tree is a rooted tree in which each node has no more than N children.
# There is no restriction on how your serialization/deserialization
# algorithm should work. You just need to ensure that an N-ary tree can be
# serialized to a string and this string can be deserialized to the
# original tree structure.
#
# For example, you may serialize the following 3-ary tree
#
# as [1 [3[5 6] 2 4]]. Note that this is just an example, you do not
# necessarily need to follow this format.
#
# Or you can follow LeetCode's level order traversal serialization format,
# where each group of children is separated by the null value.
#
# For example, the above tree may be serialized as
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14].
#
# You do not necessarily need to follow the above-suggested formats, there
# are many more different formats that work so please be creative and come
# up with different approaches yourself.
#
# Example 1:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output:
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
#
# Example 2:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: [1,null,3,2,4,null,5,6]
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

from collections import deque
from typing import List, Optional


# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List["Node"]] = None):
        self.val = val
        self.children = children if children is not None else []


class Codec:
    def serialize(self, root: "Node") -> str:
        """
        Interview explanation:
        Level-order encode: for each node emit val and child count, then its
        children in order. Empty tree -> empty string.

        Algorithm:
        - BFS queue; for each node append f"{val},{len(children)}" then enqueue kids.
        - Join tokens with spaces.

        Complexity: O(n) time and space.
        """
        if not root:
            return ""
        parts = []
        q = deque([root])
        while q:
            node = q.popleft()
            parts.append(f"{node.val},{len(node.children)}")
            for ch in node.children:
                q.append(ch)
        return " ".join(parts)

    def deserialize(self, data: str) -> "Node":
        """
        Interview explanation:
        Rebuild from BFS tokens: parse val and child-count; create that many
        placeholder children from subsequent tokens in queue order.

        Algorithm:
        - Split tokens; root from first; queue of (node, child_count); attach
          next tokens as children.

        Complexity: O(n) time and space.
        """
        if not data:
            return None
        tokens = data.split()
        val, cnt = tokens[0].split(",")
        root = Node(int(val), [])
        q = deque([(root, int(cnt))])
        i = 1
        while q:
            node, need = q.popleft()
            for _ in range(need):
                v, c = tokens[i].split(",")
                i += 1
                child = Node(int(v), [])
                node.children.append(child)
                q.append((child, int(c)))
        return root


# Your Codec object will be instantiated and called as such:
# codec = Codec()
# codec.deserialize(codec.serialize(root))
# @lc code=end
