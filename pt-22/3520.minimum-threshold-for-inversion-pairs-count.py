#
# @lc app=leetcode id=3520 lang=python3
#
# [3520] Minimum Threshold for Inversion Pairs Count
#
# https://leetcode.com/problems/minimum-threshold-for-inversion-pairs-count/description/
#
# algorithms
# Medium (54.46%)
# Likes:    3
# Dislikes: 1
# Total Accepted:    733
# Total Submissions: 1.3K
# Testcase Example:  "[1,2,3,4,3,2,1]\n7"
#
#
# You are given an array of integers nums and an integer k.
#
# An inversion pair with a threshold x is defined as a pair of indices (i,
# j) such that:
#
# i < j
#
# nums[i] > nums[j]
#
# The difference between the two numbers is at most x (i.e. nums[i] -
# nums[j] <= x).
#
# Your task is to determine the minimum integer min_threshold such that
# there are at least k inversion pairs with threshold min_threshold.
#
# If no such integer exists, return -1.
#
# Example 1:
#
# Input: nums = [1,2,3,4,3,2,1], k = 7
#
# Output: 2
#
# Explanation:
#
# For threshold x = 2, the pairs are:
#
# (3, 4) where nums[3] == 4 and nums[4] == 3.
#
# (2, 5) where nums[2] == 3 and nums[5] == 2.
#
# (3, 5) where nums[3] == 4 and nums[5] == 2.
#
# (4, 5) where nums[4] == 3 and nums[5] == 2.
#
# (1, 6) where nums[1] == 2 and nums[6] == 1.
#
# (2, 6) where nums[2] == 3 and nums[6] == 1.
#
# (4, 6) where nums[4] == 3 and nums[6] == 1.
#
# (5, 6) where nums[5] == 2 and nums[6] == 1.
#
# There are less than k inversion pairs if we choose any integer less than
# 2 as threshold.
#
# Example 2:
#
# Input: nums = [10,9,9,9,1], k = 4
#
# Output: 8
#
# Explanation:
#
# For threshold x = 8, the pairs are:
#
# (0, 1) where nums[0] == 10 and nums[1] == 9.
#
# (0, 2) where nums[0] == 10 and nums[2] == 9.
#
# (0, 3) where nums[0] == 10 and nums[3] == 9.
#
# (1, 4) where nums[1] == 9 and nums[4] == 1.
#
# (2, 4) where nums[2] == 9 and nums[4] == 1.
#
# (3, 4) where nums[3] == 9 and nums[4] == 1.
#
# There are less than k inversion pairs if we choose any integer less than
# 8 as threshold.
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^9
#

# @lc code=start
from typing import List
import bisect


class Fenwick:
    def __init__(self, n: int):
        self.n = n
        self.bit = [0] * (n + 1)

    def add(self, i: int, v: int = 1) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        while i <= self.n:
            self.bit[i] += v
            i += i & -i

    def sum(self, i: int) -> int:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        if l > r:
            return 0
        return self.sum(r) - self.sum(l - 1)


class Solution:
    def minThreshold(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count inversions (i < j, nums[i] > nums[j]) with difference <= x.
        Monotone in x — binary search the minimum threshold with >= k such pairs.

        Algorithm:
        - Binary search x in [0, max(nums)].
        - For a candidate, scan left→right; Fenwick counts prior values in
          (nums[j], nums[j]+x]; then insert nums[j] (coordinate-compressed).

        Complexity: O(n log n log A) time, O(n) space.
        """
        mx = max(nums)
        vals = sorted(set(nums))
        rank = {v: i + 1 for i, v in enumerate(vals)}
        m = len(vals)

        def count_with(threshold: int) -> int:
            bit = Fenwick(m)
            inv = 0
            for v in nums:
                lo = bisect.bisect_right(vals, v)
                hi = bisect.bisect_right(vals, v + threshold)
                if lo < hi:
                    inv += bit.range_sum(lo + 1, hi)
                bit.add(rank[v])
                if inv >= k:
                    return inv
            return inv

        lo, hi = 0, mx + 1
        while lo < hi:
            mid = (lo + hi) // 2
            if count_with(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return -1 if lo > mx else lo
# @lc code=end

