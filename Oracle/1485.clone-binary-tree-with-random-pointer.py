#
# @lc app=leetcode id=1485 lang=python3
#
# [1485] Clone Binary Tree With Random Pointer
#
# https://leetcode.com/problems/clone-binary-tree-with-random-pointer/description/
#
# algorithms
# Medium (81.28%)
# Likes:    433
# Dislikes: 98
# Total Accepted:    38.3K
# Total Submissions: 47.1K
# Testcase Example:  "[[1,null],null,[4,3],[7,0]]"
#
#
# A binary tree is given such that each node contains an additional random
# pointer which could point to any node in the tree or null.
#
# Return a deep copy of the tree.
#
# The tree is represented in the same input/output way as normal binary
# trees where each node is represented as a pair of [val, random_index]
# where:
#
# val: an integer representing Node.val
#
# random_index: the index of the node (in the input) where the random
# pointer points to, or null if it does not point to any node.
#
# You will be given the tree in class Node and you should return the
# cloned tree in class NodeCopy. NodeCopy class is just a clone of Node
# class with the same attributes and constructors.
#
# Example 1:
#
# Input: root = [[1,null],null,[4,3],[7,0]]
# Output: [[1,null],null,[4,3],[7,0]]
# Explanation: The original binary tree is [1,null,4,7].
# The random pointer of node one is null, so it is represented as [1,
# null].
# The random pointer of node 4 is node 7, so it is represented as [4, 3]
# where 3 is the index of node 7 in the array representing the tree.
# The random pointer of node 7 is node 1, so it is represented as [7, 0]
# where 0 is the index of node 1 in the array representing the tree.
#
# Example 2:
#
# Input: root = [[1,4],null,[1,0],null,[1,5],[1,5]]
# Output: [[1,4],null,[1,0],null,[1,5],[1,5]]
# Explanation: The random pointer of a node can be the node itself.
#
# Example 3:
#
# Input: root = [[1,6],[2,5],[3,4],[4,3],[5,2],[6,1],[7,0]]
# Output: [[1,6],[2,5],[3,4],[4,3],[5,2],[6,1],[7,0]]
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 1000].
#
# 1 <= Node.val <= 10^6
#
# @lc code=start
from typing import Optional

# Definition for Node.
class Node:
    def __init__(self, val=0, left=None, right=None, random=None):
        self.val = val
        self.left = left
        self.right = right
        self.random = random


class NodeCopy:
    def __init__(self, val=0, left=None, right=None, random=None):
        self.val = val
        self.left = left
        self.right = right
        self.random = random


class Solution:
    def copyRandomBinaryTree(self, root: "Optional[Node]") -> "Optional[NodeCopy]":
        """
        Interview explanation:
        Premium. Deep-copy a binary tree where each node has left, right, and
        random. Map original Node → NodeCopy; DFS clones children and random
        using the map to avoid duplicates / handle shared structure.

        Algorithm:
        - memo dict; dfs(node): if None return None; if in memo return; create
          NodeCopy; recurse left/right/random.

        Complexity: O(n) time/space.
        """
        memo = {}

        def dfs(node):
            if not node:
                return None
            if node in memo:
                return memo[node]
            copy = NodeCopy(node.val)
            memo[node] = copy
            copy.left = dfs(node.left)
            copy.right = dfs(node.right)
            copy.random = dfs(node.random)
            return copy

        return dfs(root)

    def copyRandomBinaryTree_bfs(self, root: "Optional[Node]") -> "Optional[NodeCopy]":
        """
        Interview explanation:
        Alternate: BFS two-pass — create all NodeCopy nodes, then wire
        left/right/random from the map.

        Algorithm:
        - Queue traverse originals creating copies; second pass assign pointers.

        Complexity: O(n) time/space.
        """
        if not root:
            return None
        from collections import deque

        memo = {root: NodeCopy(root.val)}
        q = deque([root])
        while q:
            node = q.popleft()
            for child in (node.left, node.right, node.random):
                if child and child not in memo:
                    memo[child] = NodeCopy(child.val)
                    q.append(child)
        for node, copy in list(memo.items()):
            copy.left = memo.get(node.left)
            copy.right = memo.get(node.right)
            copy.random = memo.get(node.random)
        return memo[root]
# @lc code=end
