#
# @lc app=leetcode id=3378 lang=python3
#
# [3378] Count Connected Components in LCM Graph
#
# https://leetcode.com/problems/count-connected-components-in-lcm-graph/description/
#
# algorithms
# Hard (31.72%)
# Likes:    85
# Dislikes: 2
# Total Accepted:    5.9K
# Total Submissions: 18.6K
# Testcase Example:  "[2,4,8,3,9]\n5"
#
#
# You are given an array of integers nums of size n and a positive integer
# threshold.
#
# There is a graph consisting of n nodes with the i^th node having a value
# of nums[i]. Two nodes i and j in the graph are connected via an
# undirected edge if lcm(nums[i], nums[j]) <= threshold.
#
# Return the number of connected components in this graph.
#
# A connected component is a subgraph of a graph in which there exists a
# path between any two vertices, and no vertex of the subgraph shares an
# edge with a vertex outside of the subgraph.
#
# The term lcm(a, b) denotes the least common multiple of a and b.
#
# Example 1:
#
# Input: nums = [2,4,8,3,9], threshold = 5
#
# Output: 4
#
# Explanation:
#
# The four connected components are (2, 4), (3), (8), (9).
#
# Example 2:
#
# Input: nums = [2,4,8,3,9,12], threshold = 10
#
# Output: 2
#
# Explanation:
#
# The two connected components are (2, 3, 4, 8, 9), and (12).
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# All elements of nums are unique.
#
# 1 <= threshold <= 2 * 10^5
#

# @lc code=start
from typing import List


class Solution:
    def countComponents(self, nums: List[int], threshold: int) -> int:
        """
        Interview explanation:
        Edge when lcm(a,b) <= threshold. Values > threshold are isolated.
        For a,b <= threshold, they connect (possibly via bridge multiples) by
        unioning each num with all its multiples up to threshold.

        Algorithm:
        - Union-Find on 0..threshold.
        - For each num <= threshold, union(num, j) for j = num, 2num, ... <= T.
        - Count distinct roots among nums (and singleton large values).

        Complexity: O(n * (T/num) + T) ~ O(T log T + n) time, O(T) space.
        """
        parent = list(range(threshold + 1))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for num in nums:
            if num > threshold:
                continue
            for j in range(num, threshold + 1, num):
                union(num, j)

        roots = set()
        for num in nums:
            if num > threshold:
                roots.add(num)
            else:
                roots.add(find(num))
        return len(roots)
# @lc code=end
