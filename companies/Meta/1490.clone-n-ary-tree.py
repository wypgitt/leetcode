#
# @lc app=leetcode id=1490 lang=python3
#
# [1490] Clone N-ary Tree
#
# https://leetcode.com/problems/clone-n-ary-tree/description/
#
# algorithms
# Medium (83.12%)
# Likes:    433
# Dislikes: 17
# Total Accepted:    36.4K
# Total Submissions: 43.8K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
#
# Given a root of an N-ary tree, return a deep copy (clone) of the tree.
#
# Each node in the n-ary tree contains a val (int) and a list (List[Node])
# of its children.
#
# class Node {
#     public int val;
#     public List<Node> children;
# }
#
# Nary-Tree input serialization is represented in their level order
# traversal, each group of children is separated by the null value (See
# examples).
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
# Constraints:
#
# The depth of the n-ary tree is less than or equal to 1000.
#
# The total number of nodes is between [0, 10^4].
#
# Follow up: Can your solution work for the graph problem?
#
# @lc code=start
from typing import Optional, List

# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List["Node"]] = None):
        self.val = val
        self.children = children if children is not None else []


class Solution:
    def cloneTree(self, root: "Optional[Node]") -> "Optional[Node]":
        """
        Interview explanation:
        Premium. Deep-clone an N-ary tree. Recursive DFS: create new node, clone
        each child.

        Algorithm:
        - If root is None return None; Node(val, [clone(c) for c in children]).

        Complexity: O(n) time/space.
        """
        if not root:
            return None
        return Node(root.val, [self.cloneTree(c) for c in root.children])

    def cloneTree_bfs(self, root: "Optional[Node]") -> "Optional[Node]":
        """
        Interview explanation:
        Alternate: BFS with map original→clone; wire children from the map.

        Algorithm:
        - Queue; for each node create clone of children and enqueue.

        Complexity: O(n) time/space.
        """
        if not root:
            return None
        from collections import deque

        memo = {root: Node(root.val, [])}
        q = deque([root])
        while q:
            node = q.popleft()
            for c in node.children:
                if c not in memo:
                    memo[c] = Node(c.val, [])
                    q.append(c)
                memo[node].children.append(memo[c])
        return memo[root]
# @lc code=end
