#
# @lc app=leetcode id=444 lang=python3
#
# [444] Sequence Reconstruction
#
# https://leetcode.com/problems/sequence-reconstruction/description/
#
# algorithms
# Medium (31.04%)
# Likes:    622
# Dislikes: 1550
# Total Accepted:    66.6K
# Total Submissions: 214.7K
# Testcase Example:  "[1,2,3]\n[[1,2],[1,3]]"
#
#
# You are given an integer array nums of length n where nums is a
# permutation of the integers in the range [1, n]. You are also given a 2D
# integer array sequences where sequences[i] is a subsequence of nums.
#
# Check if nums is the shortest possible and the only supersequence. The
# shortest supersequence is a sequence with the shortest length and has
# all sequences[i] as subsequences. There could be multiple valid
# supersequences for the given array sequences.
#
# For example, for sequences = [[1,2],[1,3]], there are two shortest
# supersequences, [1,2,3] and [1,3,2].
#
# While for sequences = [[1,2],[1,3],[1,2,3]], the only shortest
# supersequence possible is [1,2,3]. [1,2,3,4] is a possible supersequence
# but not the shortest.
#
# Return true if nums is the only shortest supersequence for sequences, or
# false otherwise.
#
# A subsequence is a sequence that can be derived from another sequence by
# deleting some or no elements without changing the order of the remaining
# elements.
#
# Example 1:
#
# Input: nums = [1,2,3], sequences = [[1,2],[1,3]]
# Output: false
# Explanation: There are two possible supersequences: [1,2,3] and [1,3,2].
# The sequence [1,2] is a subsequence of both: [1,2,3] and [1,3,2].
# The sequence [1,3] is a subsequence of both: [1,2,3] and [1,3,2].
# Since nums is not the only shortest supersequence, we return false.
#
# Example 2:
#
# Input: nums = [1,2,3], sequences = [[1,2]]
# Output: false
# Explanation: The shortest possible supersequence is [1,2].
# The sequence [1,2] is a subsequence of it: [1,2].
# Since nums is not the shortest supersequence, we return false.
#
# Example 3:
#
# Input: nums = [1,2,3], sequences = [[1,2],[1,3],[2,3]]
# Output: true
# Explanation: The shortest possible supersequence is [1,2,3].
# The sequence [1,2] is a subsequence of it: [1,2,3].
# The sequence [1,3] is a subsequence of it: [1,2,3].
# The sequence [2,3] is a subsequence of it: [1,2,3].
# Since nums is the only shortest supersequence, we return true.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^4
#
# nums is a permutation of all the integers in the range [1, n].
#
# 1 <= sequences.length <= 10^4
#
# 1 <= sequences[i].length <= 10^4
#
# 1 <= sum(sequences[i].length) <= 10^5
#
# 1 <= sequences[i][j] <= n
#
# All the arrays of sequences are unique.
#
# sequences[i] is a subsequence of nums.
#
# @lc code=start

from collections import defaultdict, deque
from typing import Dict, List, Set


class Solution:
    def sequenceReconstruction(self, nums: List[int], sequences: List[List[int]]) -> bool:
        """
        Interview explanation:
        Topological uniqueness: build a DAG from consecutive pairs in sequences.
        nums is the unique shortest supersequence iff there is exactly one valid
        topo order equal to nums (always exactly one node with indegree 0).

        Algorithm:
        - Build adjacency + indegree from consecutive pairs.
        - Kahn BFS: at every step queue size must be exactly 1; order must match nums.

        Complexity: O(n + e) time/space.
        """
        n = len(nums)
        graph: Dict[int, Set[int]] = {i: set() for i in range(1, n + 1)}
        indeg = [0] * (n + 1)
        for seq in sequences:
            for a, b in zip(seq, seq[1:]):
                if b not in graph[a]:
                    graph[a].add(b)
                    indeg[b] += 1
        q = deque([i for i in range(1, n + 1) if indeg[i] == 0])
        order = []
        while q:
            if len(q) != 1:
                return False
            u = q.popleft()
            order.append(u)
            for v in graph[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        return order == nums
# @lc code=end
