#
# @lc app=leetcode id=2519 lang=python3
#
# [2519] Count the Number of K-Big Indices
#
# https://leetcode.com/problems/count-the-number-of-k-big-indices/description/
#
# algorithms
# Hard (53.57%)
# Likes:    114
# Dislikes: 24
# Total Accepted:    9.8K
# Total Submissions: 18.4K
# Testcase Example:  "[2,3,6,5,2,3]\n2"
#
#
# You are given a 0-indexed integer array nums and a positive integer k.
#
# We call an index i k-big if the following conditions are satisfied:
#
# There exist at least k different indices idx1 such that idx1 < i and
# nums[idx1] < nums[i].
#
# There exist at least k different indices idx2 such that idx2 > i and
# nums[idx2] < nums[i].
#
# Return the number of k-big indices.
#
# Example 1:
#
# Input: nums = [2,3,6,5,2,3], k = 2
# Output: 2
# Explanation: There are only two 2-big indices in nums:
# - i = 2 --> There are two valid idx1: 0 and 1. There are three valid
# idx2: 2, 3, and 4.
# - i = 3 --> There are two valid idx1: 0 and 1. There are two valid idx2:
# 3 and 4.
#
# Example 2:
#
# Input: nums = [1,1,1], k = 3
# Output: 0
# Explanation: There are no 3-big indices in nums.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i], k <= nums.length
#
# @lc code=start
from typing import List


class Fenwick:
    def __init__(self, n: int):
        """
        Interview explanation:
        Binary Indexed Tree for prefix frequency sums (1-indexed ranks).

        Algorithm:
        - add/query via lowbit jumps.

        Complexity: O(log n) per op, O(n) space.
        """
        self.n = n
        self.bit = [0] * (n + 1)

    def add(self, i: int, delta: int = 1) -> None:
        """
        Interview explanation:
        Add delta at rank i.

        Algorithm:
        - Walk i += lowbit(i).

        Complexity: O(log n) time, O(1) space.
        """
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def prefix(self, i: int) -> int:
        """
        Interview explanation:
        Sum of frequencies in ranks [1, i].

        Algorithm:
        - Walk i -= lowbit(i).

        Complexity: O(log n) time, O(1) space.
        """
        s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s


class Solution:
    def kBigIndices(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Index i is k-big if >= k smaller elements exist to the left and to the
        right. Count such indices.

        Algorithm:
        (Fenwick / BIT)
        - Coordinate-compress values.
        - Left-to-right BIT: count strictly smaller on left per index.
        - Right-to-left BIT: count strictly smaller on right; add if both >= k.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        ranks = {v: i + 1 for i, v in enumerate(sorted(set(nums)))}
        m = len(ranks)

        left_smaller = [0] * n
        bit = Fenwick(m)
        for i, x in enumerate(nums):
            r = ranks[x]
            left_smaller[i] = bit.prefix(r - 1)
            bit.add(r)

        bit = Fenwick(m)
        ans = 0
        for i in range(n - 1, -1, -1):
            r = ranks[nums[i]]
            right_smaller = bit.prefix(r - 1)
            if left_smaller[i] >= k and right_smaller >= k:
                ans += 1
            bit.add(r)
        return ans
# @lc code=end
