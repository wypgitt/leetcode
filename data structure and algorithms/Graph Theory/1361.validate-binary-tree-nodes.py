#
# @lc app=leetcode id=1361 lang=python3
#
# [1361] Validate Binary Tree Nodes
#
# https://leetcode.com/problems/validate-binary-tree-nodes/description/
#
# algorithms
# Medium (44.18%)
# Likes:    2263
# Dislikes: 525
# Total Accepted:    139K
# Total Submissions: 314K
# Testcase Example:  "4"
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
# Example 1:
#
# Input: n = 4, leftChild = [1,-1,3,-1], rightChild = [2,-1,-1,-1]
# Output: true
#
# Example 2:
#
# Input: n = 4, leftChild = [1,-1,3,-1], rightChild = [2,3,-1,-1]
# Output: false
#
# Example 3:
#
# Input: n = 2, leftChild = [1,0], rightChild = [-1,-1]
# Output: false
#
# Constraints:
#
# n == leftChild.length == rightChild.length
#
# 1 <= n <= 10^4
#
# -1 <= leftChild[i], rightChild[i] <= n - 1
#

# @lc code=start

from collections import deque
from typing import List


class Solution:
    def validateBinaryTreeNodes(self, n: int, leftChild: List[int], rightChild: List[int]) -> bool:
        """
        Interview explanation:
        Valid binary tree: exactly one root (indegree 0), all nodes reachable,
        no node with indegree >1, and no cycles.

        Algorithm:
        - Compute indegrees from children arrays; find unique root
        - BFS/DFS from root; visit exactly n nodes

        Complexity: O(n) time, O(n) space.
        """
        indeg = [0] * n
        for i in range(n):
            for c in (leftChild[i], rightChild[i]):
                if c != -1:
                    indeg[c] += 1
                    if indeg[c] > 1:
                        return False
        roots = [i for i in range(n) if indeg[i] == 0]
        if len(roots) != 1:
            return False
        root = roots[0]
        seen = 0
        q = deque([root])
        vis = [False] * n
        vis[root] = True
        while q:
            u = q.popleft()
            seen += 1
            for c in (leftChild[u], rightChild[u]):
                if c == -1:
                    continue
                if vis[c]:
                    return False
                vis[c] = True
                q.append(c)
        return seen == n

    def validateBinaryTreeNodes_dfs(self, n: int, leftChild: List[int], rightChild: List[int]) -> bool:
        """
        Interview explanation:
        Alternate DFS reachability from the unique root after indegree checks.

        Algorithm:
        - Same indegree/root validation; DFS count visited nodes == n

        Complexity: O(n) time, O(n) space.
        """
        indeg = [0] * n
        for i in range(n):
            for c in (leftChild[i], rightChild[i]):
                if c != -1:
                    indeg[c] += 1
                    if indeg[c] > 1:
                        return False
        roots = [i for i in range(n) if indeg[i] == 0]
        if len(roots) != 1:
            return False
        vis = set()

        def dfs(u: int) -> None:
            if u in vis:
                return
            vis.add(u)
            for c in (leftChild[u], rightChild[u]):
                if c != -1:
                    dfs(c)

        dfs(roots[0])
        return len(vis) == n
# @lc code=end
