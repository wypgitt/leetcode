#
# @lc app=leetcode id=1042 lang=python3
#
# [1042] Flower Planting With No Adjacent
#
# https://leetcode.com/problems/flower-planting-with-no-adjacent/description/
#
# algorithms
# Medium (53.62%)
# Likes:    1575
# Dislikes: 727
# Total Accepted:    104.6K
# Total Submissions: 194.9K
# Testcase Example:  '3\n[[1,2],[2,3],[3,1]]'
#
# You have n gardens, labeled from 1 to n, and an array paths where paths[i] =
# [xi, yi] describes a bidirectional path between garden xi to garden yi. In
# each garden, you want to plant one of 4 types of flowers.
# 
# All gardens have at most 3 paths coming into or leaving it.
# 
# Your task is to choose a flower type for each garden such that, for any two
# gardens connected by a path, they have different types of flowers.
# 
# Return any such a choice as an array answer, where answer[i] is the type of
# flower planted in the (i+1)^th garden. The flower types are denoted 1, 2, 3,
# or 4. It is guaranteed an answer exists.
# 
# 
# Example 1:
# 
# 
# Input: n = 3, paths = [[1,2],[2,3],[3,1]]
# Output: [1,2,3]
# Explanation:
# Gardens 1 and 2 have different types.
# Gardens 2 and 3 have different types.
# Gardens 3 and 1 have different types.
# Hence, [1,2,3] is a valid answer. Other valid answers include [1,2,4],
# [1,4,2], and [3,2,1].
# 
# 
# Example 2:
# 
# 
# Input: n = 4, paths = [[1,2],[3,4]]
# Output: [1,2,1,2]
# 
# 
# Example 3:
# 
# 
# Input: n = 4, paths = [[1,2],[2,3],[3,4],[4,1],[1,3],[2,4]]
# Output: [1,2,3,4]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^4
# 0 <= paths.length <= 2 * 10^4
# paths[i].length == 2
# 1 <= xi, yi <= n
# xi != yi
# Every garden has at most 3 paths coming into or leaving it.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def gardenNoAdj(self, n: int, paths: List[List[int]]) -> List[int]:
        graph = [[] for _ in range(n)]
        for x, y in paths:
            graph[x - 1].append(y - 1)
            graph[y - 1].append(x - 1)

        answer = [0] * n
        for garden in range(n):
            used = {answer[neighbor] for neighbor in graph[garden]}
            for flower in range(1, 5):
                if flower not in used:
                    answer[garden] = flower
                    break

        return answer
# @lc code=end

"""
Interview Explanation

Core idea:
Each garden has degree at most 3, but there are 4 flower types. When we visit a
garden, at most three neighbor colors can be forbidden, so at least one color
is always available.

Algorithm:
1. Build a 0-indexed adjacency list.
2. Visit gardens in any order.
3. Collect colors already assigned to its neighbors.
4. Pick the first flower type from 1 to 4 that is not used.

Data structure choice:
An adjacency list is natural for sparse graph coloring. A set of neighbor
colors makes membership checks constant time and stays tiny because degree is
at most 3.

Correctness:
When a garden is colored, none of its already-colored neighbors receive the
same color. Future neighbors will also check this garden's color before
choosing theirs. Because a garden has at most 3 neighbors and 4 colors exist,
the greedy choice always finds a valid color. Thus every edge ends with two
different flower types.

Complexity:
Building and scanning the graph costs O(n + p), where p is len(paths). Space is
O(n + p).

Tests and edge cases:
- No paths: every garden can receive color 1.
- Triangle: uses three distinct colors.
- Complete graph on four gardens: uses all four colors.
- 1-indexed input labels are converted to 0-indexed array positions.
"""
