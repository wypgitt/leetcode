#
# @lc app=leetcode id=1273 lang=python3
#
# [1273] Delete Tree Nodes
#
# https://leetcode.com/problems/delete-tree-nodes/description/
#
# algorithms
# Medium (61.56%)
# Likes:    235
# Dislikes: 66
# Total Accepted:    11.7K
# Total Submissions: 19K
# Testcase Example:  "7\n[-1,0,0,1,2,2,2]\n[1,-2,4,0,-2,-1,-1]"
#
#
# A tree rooted at node 0 is given as follows:
#
# The number of nodes is nodes;
#
# The value of the i^th node is value[i];
#
# The parent of the i^th node is parent[i].
#
# Remove every subtree whose sum of values of nodes is zero.
#
# Return the number of the remaining nodes in the tree.
#
# Example 1:
#
# Input: nodes = 7, parent = [-1,0,0,1,2,2,2], value = [1,-2,4,0,-2,-1,-1]
# Output: 2
#
# Example 2:
#
# Input: nodes = 7, parent = [-1,0,0,1,2,2,2], value = [1,-2,4,0,-2,-1,-2]
# Output: 6
#
# Constraints:
#
# 1 <= nodes <= 10^4
#
# parent.length == nodes
#
# 0 <= parent[i] <= nodes - 1
#
# parent[0] == -1 which indicates that 0 is the root.
#
# value.length == nodes
#
# -10^5 <= value[i] <= 10^5
#
# The given input is guaranteed to represent a valid tree.
#
# @lc code=start

from typing import List
from collections import defaultdict


class Solution:
    def deleteTreeNodes(self, nodes: int, parent: List[int], value: List[int]) -> int:
        """
        Interview explanation:
        Premium. Forest rooted at 0 (parent[i]). Delete every subtree whose
        sum is 0 (and all nodes under it). Postorder: return (sum, count) of
        surviving nodes; if sum==0, contribute 0 nodes.

        Algorithm:
        - Build children lists from parent.
        - DFS(u): s=value[u], c=1; for child: add child's (s,c); if s==0
          return (0,0) else (s,c).
        - Answer = count from DFS(0).

        Complexity: O(n) time and space.
        """
        children = defaultdict(list)
        root = 0
        for i, p in enumerate(parent):
            if p == -1:
                root = i
            else:
                children[p].append(i)

        def dfs(u: int):
            s, c = value[u], 1
            for v in children[u]:
                cs, cc = dfs(v)
                s += cs
                c += cc
            if s == 0:
                return 0, 0
            return s, c

        return dfs(root)[1]
# @lc code=end
