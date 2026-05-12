#
# @lc app=leetcode id=1273 lang=python3
#
# [1273] Delete Tree Nodes
#
# https://leetcode.com/problems/delete-tree-nodes/description/
#
# algorithms
# Medium (61.66%)
# Likes:    235
# Dislikes: 66
# Total Accepted:    11.6K
# Total Submissions: 18.8K
# Testcase Example:  '7\n[-1,0,0,1,2,2,2]\n[1,-2,4,0,-2,-1,-1]'
#
# A tree rooted at node 0 is given as follows:
# 
# 
# The number of nodes is nodes;
# The value of the i^th node is value[i];
# The parent of the i^th node is parent[i].
# 
# 
# Remove every subtree whose sum of values of nodes is zero.
# 
# Return the number of the remaining nodes in the tree.
# 
# 
# Example 1:
# 
# 
# Input: nodes = 7, parent = [-1,0,0,1,2,2,2], value = [1,-2,4,0,-2,-1,-1]
# Output: 2
# 
# 
# Example 2:
# 
# 
# Input: nodes = 7, parent = [-1,0,0,1,2,2,2], value = [1,-2,4,0,-2,-1,-2]
# Output: 6
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nodes <= 10^4
# parent.length == nodes
# 0 <= parent[i] <= nodes - 1
# parent[0] == -1 which indicates that 0 is the root.
# value.length == nodes
# -10^5 <= value[i] <= 10^5
# The given input is guaranteed to represent a valid tree.
# 
# 
#

# @lc code=start
import sys
from collections import defaultdict
from typing import List


class Solution:
    def deleteTreeNodes(self, nodes: int, parent: List[int], value: List[int]) -> int:
        sys.setrecursionlimit(max(1000, nodes + 10))
        children = defaultdict(list)
        root = 0

        for node, par in enumerate(parent):
            if par == -1:
                root = node
            else:
                children[par].append(node)

        def dfs(node: int) -> tuple[int, int]:
            subtree_sum = value[node]
            count = 1

            for child in children[node]:
                child_sum, child_count = dfs(child)
                subtree_sum += child_sum
                count += child_count

            if subtree_sum == 0:
                return 0, 0
            return subtree_sum, count

        return dfs(root)[1]
# @lc code=end

# Explanation
# -----------
# Build a child adjacency list from the parent array. A postorder DFS computes
# both subtree sum and remaining node count. If a subtree sum is 0, the whole
# subtree is deleted, so it contributes sum 0 and count 0 to its parent.
#
# Postorder is required because whether a node survives depends on the total
# value of all descendants. The adjacency list turns the parent array into the
# natural tree traversal format.
#
# Edge cases: the root subtree can sum to zero, returning 0; multiple nested
# zero-sum subtrees; negative values are handled by normal addition.
#
# Time complexity: O(n), one DFS visit per node.
# Space complexity: O(n) for children and recursion stack.
