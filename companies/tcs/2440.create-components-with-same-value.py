#
# @lc app=leetcode id=2440 lang=python3
#
# [2440] Create Components With Same Value
#
# https://leetcode.com/problems/create-components-with-same-value/description/
#
# algorithms
# Hard (53.97%)
# Likes:    446
# Dislikes: 7
# Total Accepted:    11.8K
# Total Submissions: 21.9K
# Testcase Example:  "[6,2,2,2,6]\n[[0,1],[1,2],[1,3],[3,4]]"
#
# There is an undirected tree with n nodes labeled from 0 to n - 1.
#
# You are given a 0-indexed integer array nums of length n where nums[i]
# represents the value of the i^th node. You are also given a 2D integer array
# edges of length n - 1 where edges[i] = [a_i, b_i] indicates that there is an
# edge between nodes a_i and b_i in the tree.
#
# You are allowed to delete some edges, splitting the tree into multiple
# connected components. Let the value of a component be the sum of all nums[i]
# for which node i is in the component.
#
# Return the maximum number of edges you can delete, such that every connected
# component in the tree has the same value.
#
#
#
# Example 1:
#
# Input: nums = [6,2,2,2,6], edges = [[0,1],[1,2],[1,3],[3,4]]
# Output: 2
# Explanation: The above figure shows how we can delete the edges [0,1] and
# [3,4]. The created components are nodes [0], [1,2,3] and [4]. The sum of the
# values in each component equals 6. It can be proven that no better deletion
# exists, so the answer is 2.
#
# Example 2:
#
# Input: nums = [2], edges = []
# Output: 0
# Explanation: There are no edges to be deleted.
#
#
#
# Constraints:
#
#
# 1 <= n <= 2 * 10^4
#
#
# nums.length == n
#
#
# 1 <= nums[i] <= 50
#
#
# edges.length == n - 1
#
#
# edges[i].length == 2
#
#
# 0 <= edges[i][0], edges[i][1] <= n - 1
#
#
# edges represents a valid tree.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def componentValue(self, nums: List[int], edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Delete tree edges so every component has equal sum; maximize deletions.

        Algorithm:
        - Try component counts from n down; if total % parts==0 and DFS can cut
          subtrees of sum total/parts, return parts-1.

        Complexity: O(n * #divisors) time, O(n) space.
        """
        n = len(nums)
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        total = sum(nums)

        def check(target: int) -> bool:
            def dfs(u: int, p: int) -> int:
                s = nums[u]
                for v in g[u]:
                    if v == p:
                        continue
                    sub = dfs(v, u)
                    if sub < 0:
                        return -1
                    s += sub
                if s == target:
                    return 0
                if s > target:
                    return -1
                return s

            return dfs(0, -1) == 0

        for parts in range(n, 0, -1):
            if total % parts == 0 and check(total // parts):
                return parts - 1
        return 0
# @lc code=end
