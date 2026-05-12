#
# @lc app=leetcode id=1361 lang=python3
#
# [1361] Validate Binary Tree Nodes
#
# https://leetcode.com/problems/validate-binary-tree-nodes/description/
#
# algorithms
# Medium (44.11%)
# Likes:    2255
# Dislikes: 525
# Total Accepted:    136.2K
# Total Submissions: 308.7K
# Testcase Example:  '4\n[1,-1,3,-1]\n[2,-1,-1,-1]'
#
# You have n binary tree nodes numbered from 0 to n - 1 where node i has two
# children leftChild[i] and rightChild[i], return true if and only if all the
# given nodes form exactly one valid binary tree.
# 
# If node i has no left child then leftChild[i] will equal -1, similarly for
# the right child.
# 
# Note that the nodes have no values and that we only use the node numbers in
# this problem.
# 
# 
# Example 1:
# 
# 
# Input: n = 4, leftChild = [1,-1,3,-1], rightChild = [2,-1,-1,-1]
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: n = 4, leftChild = [1,-1,3,-1], rightChild = [2,3,-1,-1]
# Output: false
# 
# 
# Example 3:
# 
# 
# Input: n = 2, leftChild = [1,0], rightChild = [-1,-1]
# Output: false
# 
# 
# 
# Constraints:
# 
# 
# n == leftChild.length == rightChild.length
# 1 <= n <= 10^4
# -1 <= leftChild[i], rightChild[i] <= n - 1
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def validateBinaryTreeNodes(self, n: int, leftChild: List[int], rightChild: List[int]) -> bool:
        indegree = [0] * n

        for parent in range(n):
            for child in (leftChild[parent], rightChild[parent]):
                if child == -1:
                    continue
                indegree[child] += 1
                if indegree[child] > 1:
                    return False

        roots = [node for node in range(n) if indegree[node] == 0]
        if len(roots) != 1:
            return False

        root = roots[0]
        seen = set()
        stack = [root]

        while stack:
            node = stack.pop()
            if node in seen:
                return False
            seen.add(node)

            if leftChild[node] != -1:
                stack.append(leftChild[node])
            if rightChild[node] != -1:
                stack.append(rightChild[node])

        return len(seen) == n
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# A valid binary tree over `n` labeled nodes must have exactly one root, every
# non-root node must have exactly one parent, and all nodes must be reachable
# from that root with no cycles.
#
# Data structures:
# - `indegree` counts how many parents each node has.
# - A DFS stack verifies reachability and catches cycles/revisits.
#
# Walkthrough:
# 1. Count incoming edges from all left and right child pointers.
# 2. If any node has indegree > 1, it has multiple parents, so invalid.
# 3. There must be exactly one node with indegree 0; that is the root.
# 4. DFS from the root. Revisiting a node means a cycle or duplicate path.
# 5. The DFS must visit all `n` nodes.
#
# Edge cases:
# - Two disconnected trees: more than one root or not all nodes visited.
# - Cycle: either no root exists or DFS detects a revisit.
# - Single node with no children: one root and one visited node, valid.
#
# Complexity:
# - Time: O(n).
# - Space: O(n).
