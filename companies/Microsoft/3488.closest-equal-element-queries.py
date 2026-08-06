#
# @lc app=leetcode id=3488 lang=python3
#
# [3488] Closest Equal Element Queries
#
# https://leetcode.com/problems/closest-equal-element-queries/description/
#
# algorithms
# Medium (51.35%)
# Likes:    513
# Dislikes: 35
# Total Accepted:    104.6K
# Total Submissions: 203.7K
# Testcase Example:  "[1,3,1,4,1,3,2]\n[0,3,5]"
#
#
# You are given a circular array nums and an array queries.
#
# For each query i, you have to find the following:
#
# The minimum distance between the element at index queries[i] and any
# other index j in the circular array, where nums[j] == nums[queries[i]].
# If no such index exists, the answer for that query should be -1.
#
# Return an array answer of the same size as queries, where answer[i]
# represents the result for query i.
#
# Example 1:
#
# Input: nums = [1,3,1,4,1,3,2], queries = [0,3,5]
#
# Output: [2,-1,3]
#
# Explanation:
#
# Query 0: The element at queries[0] = 0 is nums[0] = 1. The nearest index
# with the same value is 2, and the distance between them is 2.
#
# Query 1: The element at queries[1] = 3 is nums[3] = 4. No other index
# contains 4, so the result is -1.
#
# Query 2: The element at queries[2] = 5 is nums[5] = 3. The nearest index
# with the same value is 1, and the distance between them is 3 (following
# the circular path: 5 -> 6 -> 0 -> 1).
#
# Example 2:
#
# Input: nums = [1,2,3,4], queries = [0,1,2,3]
#
# Output: [-1,-1,-1,-1]
#
# Explanation:
#
# Each value in nums is unique, so no index shares the same value as the
# queried element. This results in -1 for all queries.
#
# Constraints:
#
# 1 <= queries.length <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# 0 <= queries[i] < nums.length
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def solveQueries(self, nums: List[int], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        Circular array: for each query index, find the nearest other index with
        the same value (min circular distance), or -1 if unique.

        Algorithm:
        - Group indices by value (sorted).
        - For each index, compare distance to previous/next occurrence in the
          group (wrapping around).

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(nums)
        pos = defaultdict(list)
        for i, x in enumerate(nums):
            pos[x].append(i)

        nearest = [-1] * n
        for idxs in pos.values():
            m = len(idxs)
            if m == 1:
                continue
            for t, i in enumerate(idxs):
                prv = idxs[t - 1]
                nxt = idxs[(t + 1) % m]
                d_prev = (i - prv) % n
                d_next = (nxt - i) % n
                nearest[i] = min(d_prev, d_next)

        return [nearest[q] for q in queries]
# @lc code=end
