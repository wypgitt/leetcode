#
# @lc app=leetcode id=3486 lang=python3
#
# [3486] Longest Special Path II
#
# https://leetcode.com/problems/longest-special-path-ii/description/
#
# algorithms
# Hard (20.03%)
# Likes:    36
# Dislikes: 6
# Total Accepted:    2.8K
# Total Submissions: 14K
# Testcase Example:  "[[0,1,1],[1,2,3],[1,3,1],[2,4,6],[4,7,2],[3,5,2],[3,6,5],[6,8,3]]\n[1,1,0,3,1,2,1,1,0]"
#
#
# You are given an undirected tree rooted at node 0, with n nodes numbered
# from 0 to n - 1. This is represented by a 2D array edges of length n -
# 1, where edges[i] = [u_i, v_i, length_i] indicates an edge between nodes
# u_i and v_i with length length_i. You are also given an integer array
# nums, where nums[i] represents the value at node i.
#
# A special path is defined as a downward path from an ancestor node to a
# descendant node in which all node values are distinct, except for at
# most one value that may appear twice.
#
# Return an array result of size 2, where result[0] is the length of the
# longest special path, and result[1] is the minimum number of nodes in
# all possible longest special paths.
#
# Example 1:
#
# Input: edges =
# [[0,1,1],[1,2,3],[1,3,1],[2,4,6],[4,7,2],[3,5,2],[3,6,5],[6,8,3]], nums
# = [1,1,0,3,1,2,1,1,0]
#
# Output: [9,3]
#
# Explanation:
#
# In the image below, nodes are colored by their corresponding values in
# nums.
#
# The longest special paths are 1 -> 2 -> 4 and 1 -> 3 -> 6 -> 8, both
# having a length of 9. The minimum number of nodes across all longest
# special paths is 3.
#
# Example 2:
#
# Input: edges = [[1,0,3],[0,2,4],[0,3,5]], nums = [1,1,0,2]
#
# Output: [5,2]
#
# Explanation:
#
# The longest path is 0 -> 3 consisting of 2 nodes with a length of 5.
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# edges.length == n - 1
#
# edges[i].length == 3
#
# 0 <= u_i, v_i < n
#
# 1 <= length_i <= 10^3
#
# nums.length == n
#
# 0 <= nums[i] <= 5 * 10^4
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def longestSpecialPath(self, edges: List[List[int]], nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Downward special path: values mostly unique, at most one value may
        repeat once. Maximize path length (edge-weight sum); among those,
        minimize node count.

        Algorithm:
        - DFS from root 0 with prefix distances and last-seen depth per value.
        - Maintain the two largest "cut" depths forced by repeats; path starts
          after the older of those two cuts (allows one duplicate).
        - Update (maxLength, minNodes) at every node.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        graph = [[] for _ in range(n)]
        for u, v, w in edges:
            graph[u].append((v, w))
            graph[v].append((u, w))

        max_length = 0
        min_nodes = 1
        prefix = [0]
        last_seen = {}

        def dfs(u: int, prev: int, left_boundary: List[int]) -> None:
            nonlocal max_length, min_nodes
            prev_depth = last_seen.get(nums[u], 0)
            last_seen[nums[u]] = len(prefix)

            if prev_depth != 0:
                left_boundary = sorted(left_boundary + [prev_depth])[-2:]

            length = prefix[-1] - prefix[left_boundary[0]]
            nodes = len(prefix) - left_boundary[0]
            if length > max_length or (length == max_length and nodes < min_nodes):
                max_length = length
                min_nodes = nodes

            for v, w in graph[u]:
                if v == prev:
                    continue
                prefix.append(prefix[-1] + w)
                dfs(v, u, left_boundary)
                prefix.pop()

            last_seen[nums[u]] = prev_depth

        dfs(0, -1, [0, 0])
        return [max_length, min_nodes]
# @lc code=end
