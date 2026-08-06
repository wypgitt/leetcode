#
# @lc app=leetcode id=2382 lang=python3
#
# [2382] Maximum Segment Sum After Removals
#
# https://leetcode.com/problems/maximum-segment-sum-after-removals/description/
#
# algorithms
# Hard (50.11%)
# Likes:    504
# Dislikes: 6
# Total Accepted:    13.1K
# Total Submissions: 26.2K
# Testcase Example:  "[1,2,5,6,1]\n[0,3,2,4,1]"
#
# You are given two 0-indexed integer arrays nums and removeQueries, both of
# length n. For the i^th query, the element in nums at the index
# removeQueries[i] is removed, splitting nums into different segments.
#
# A segment is a contiguous sequence of positive integers in nums. A segment sum
# is the sum of every element in a segment.
#
# Return an integer array answer, of length n, where answer[i] is the maximum
# segment sum after applying the i^th removal.
#
# Note: The same index will not be removed more than once.
#
#
#
# Example 1:
#
# Input: nums = [1,2,5,6,1], removeQueries = [0,3,2,4,1]
# Output: [14,7,2,2,0]
# Explanation: Using 0 to indicate a removed element, the answer is as follows:
# Query 1: Remove the 0th element, nums becomes [0,2,5,6,1] and the maximum
# segment sum is 14 for segment [2,5,6,1].
# Query 2: Remove the 3rd element, nums becomes [0,2,5,0,1] and the maximum
# segment sum is 7 for segment [2,5].
# Query 3: Remove the 2nd element, nums becomes [0,2,0,0,1] and the maximum
# segment sum is 2 for segment [2].
# Query 4: Remove the 4th element, nums becomes [0,2,0,0,0] and the maximum
# segment sum is 2 for segment [2].
# Query 5: Remove the 1st element, nums becomes [0,0,0,0,0] and the maximum
# segment sum is 0, since there are no segments.
# Finally, we return [14,7,2,2,0].
#
# Example 2:
#
# Input: nums = [3,2,11,1], removeQueries = [3,2,1,0]
# Output: [16,5,3,0]
# Explanation: Using 0 to indicate a removed element, the answer is as follows:
# Query 1: Remove the 3rd element, nums becomes [3,2,11,0] and the maximum
# segment sum is 16 for segment [3,2,11].
# Query 2: Remove the 2nd element, nums becomes [3,2,0,0] and the maximum
# segment sum is 5 for segment [3,2].
# Query 3: Remove the 1st element, nums becomes [3,0,0,0] and the maximum
# segment sum is 3 for segment [3].
# Query 4: Remove the 0th element, nums becomes [0,0,0,0] and the maximum
# segment sum is 0, since there are no segments.
# Finally, we return [16,5,3,0].
#
#
#
# Constraints:
#
#
# n == nums.length == removeQueries.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#
#
# 0 <= removeQueries[i] < n
#
#
# All the values of removeQueries are unique.
#

# @lc code=start

from typing import List


class Solution:
    def maximumSegmentSum(self, nums: List[int], removeQueries: List[int]) -> List[int]:
        """
        Interview explanation:
        Process removals in order; after each removal report max sum among
        remaining contiguous segments (0 if empty).

        Algorithm:
        - Reverse offline: start empty; add indices back (union-find with
          segment sums); track max segment sum; answer in reverse.

        Complexity: O(n α(n)) time, O(n) space.
        """
        n = len(nums)
        parent = list(range(n))
        seg = [0] * n
        present = [False] * n
        max_sum = 0

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            nonlocal max_sum
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            parent[rb] = ra
            seg[ra] += seg[rb]
            max_sum = max(max_sum, seg[ra])

        ans = [0] * n
        for qi in range(n - 1, -1, -1):
            ans[qi] = max_sum
            i = removeQueries[qi]
            present[i] = True
            seg[i] = nums[i]
            max_sum = max(max_sum, seg[i])
            if i > 0 and present[i - 1]:
                union(i, i - 1)
            if i + 1 < n and present[i + 1]:
                union(i, i + 1)
        return ans
# @lc code=end
