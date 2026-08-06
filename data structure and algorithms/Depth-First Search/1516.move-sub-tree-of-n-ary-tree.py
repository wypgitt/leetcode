#
# @lc app=leetcode id=1516 lang=python3
#
# [1516] Move Sub-Tree of N-Ary Tree
#
# https://leetcode.com/problems/move-sub-tree-of-n-ary-tree/description/
#
# algorithms
# Hard (59.81%)
# Likes:    34
# Dislikes: 67
# Total Accepted:    2.8K
# Total Submissions: 4.6K
# Testcase Example:  "[1,null,2,3,null,4,5,null,6,null,7,8]\n4\n1"
#
#
# Given the root of an N-ary tree of unique values, and two nodes of the
# tree p and q.
#
# You should move the subtree of the node p to become a direct child of
# node q. If p is already a direct child of q, do not change anything.
# Node p must be the last child in the children list of node q.
#
# Return the root of the tree after adjusting it.
#
# There are 3 cases for nodes p and q:
#
# Node q is in the sub-tree of node p.
#
# Node p is in the sub-tree of node q.
#
# Neither node p is in the sub-tree of node q nor node q is in the
# sub-tree of node p.
#
# In cases 2 and 3, you just need to move p (with its sub-tree) to be a
# child of q, but in case 1 the tree may be disconnected, thus you need to
# reconnect the tree again. Please read the examples carefully before
# solving this problem.
#
# Nary-Tree input serialization is represented in their level order
# traversal, each group of children is separated by the null value (See
# examples).
#
# For example, the above tree is serialized as
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14].
#
# Example 1:
#
# Input: root = [1,null,2,3,null,4,5,null,6,null,7,8], p = 4, q = 1
# Output: [1,null,2,3,4,null,5,null,6,null,7,8]
# Explanation: This example follows the second case as node p is in the
# sub-tree of node q. We move node p with its sub-tree to be a direct
# child of node q.
# Notice that node 4 is the last child of node 1.
#
# Example 2:
#
# Input: root = [1,null,2,3,null,4,5,null,6,null,7,8], p = 7, q = 4
# Output: [1,null,2,3,null,4,5,null,6,null,7,8]
# Explanation: Node 7 is already a direct child of node 4. We don't change
# anything.
#
# Example 3:
#
# Input: root = [1,null,2,3,null,4,5,null,6,null,7,8], p = 3, q = 8
# Output: [1,null,2,null,4,5,null,7,8,null,null,null,3,null,6]
# Explanation: This example follows case 3 because node p is not in the
# sub-tree of node q and vice-versa. We can move node 3 with its sub-tree
# and make it as node 8's child.
#
# Example 4:
#
# Input: root = [1,null,2,3,null,4], p = 1, q = 4
# Output: [4,null,1,null,2,3]
# Explanation: This example follows case 1 because node q is in the
# sub-tree of node p. Disconnect 4 with its parent and move node 1 with
# its sub-tree and make it as node 4's child.
#
# Constraints:
#
# The total number of nodes is between [2, 1000].
#
# Each node has a unique value.
#
# p != null
#
# q != null
#
# p and q are two different nodes (i.e. p != q).
#
# @lc code=start
from typing import Optional, List

try:
    Node
except NameError:

    class Node:
        def __init__(self, val: int = None, children: Optional[List["Node"]] = None):
            self.val = val
            self.children = children if children is not None else []


class Solution:
    def moveSubTree(self, root: "Node", p: "Node", q: "Node") -> "Node":
        """
        Interview explanation:
        Premium. Make p a child of q (move whole subtree). If q is inside p's
        subtree, first put q where p was, then attach p under q. No-op if p is
        already a direct child of q.

        Algorithm:
        - Build parent and child-index maps.
        - Detach p; if q under p: detach q, splice q into p's old slot (or q
          becomes root), then append p to q.children; else append p to q.

        Complexity: O(n) time, O(n) space.
        """
        if p in q.children:
            return root

        parent = {root: None}
        idx = {root: -1}

        def build(node: "Node") -> None:
            for i, ch in enumerate(node.children):
                parent[ch] = node
                idx[ch] = i
                build(ch)

        build(root)

        def under(a: "Node", b: "Node") -> bool:
            cur = b
            while cur is not None:
                if cur is a:
                    return True
                cur = parent.get(cur)
            return False

        def reindex(par: "Node") -> None:
            for i, ch in enumerate(par.children):
                idx[ch] = i

        p_par, p_idx = parent[p], idx[p]
        q_under_p = under(p, q)

        if p_par is not None:
            p_par.children.pop(p_idx)
            reindex(p_par)
            parent[p] = None

        if q_under_p:
            q_par, q_idx = parent[q], idx[q]
            if q_par is not None:
                q_par.children.pop(q_idx)
                reindex(q_par)
                parent[q] = None
            if p_par is None:
                root = q
            else:
                insert_at = p_idx
                if q_par is p_par and q_idx < p_idx:
                    insert_at = p_idx - 1
                p_par.children.insert(insert_at, q)
                parent[q] = p_par
                reindex(p_par)
            p.children = [c for c in p.children if c is not q]
            q.children.append(p)
            parent[p] = q
        else:
            q.children.append(p)
            parent[p] = q

        return root
# @lc code=end
