#
# @lc app=leetcode id=3479 lang=python3
#
# [3479] Fruits Into Baskets III
#
# https://leetcode.com/problems/fruits-into-baskets-iii/description/
#
# algorithms
# Medium (39.43%)
# Likes:    614
# Dislikes: 85
# Total Accepted:    89.2K
# Total Submissions: 226.3K
# Testcase Example:  "[4,2,5]\n[3,5,4]"
#
#
# You are given two arrays of integers, fruits and baskets, each of length
# n, where fruits[i] represents the quantity of the i^th type of fruit,
# and baskets[j] represents the capacity of the j^th basket.
#
# From left to right, place the fruits according to these rules:
#
# Each fruit type must be placed in the leftmost available basket with a
# capacity greater than or equal to the quantity of that fruit type.
#
# Each basket can hold only one type of fruit.
#
# If a fruit type cannot be placed in any basket, it remains unplaced.
#
# Return the number of fruit types that remain unplaced after all possible
# allocations are made.
#
# Example 1:
#
# Input: fruits = [4,2,5], baskets = [3,5,4]
#
# Output: 1
#
# Explanation:
#
# fruits[0] = 4 is placed in baskets[1] = 5.
#
# fruits[1] = 2 is placed in baskets[0] = 3.
#
# fruits[2] = 5 cannot be placed in baskets[2] = 4.
#
# Since one fruit type remains unplaced, we return 1.
#
# Example 2:
#
# Input: fruits = [3,6,1], baskets = [6,4,7]
#
# Output: 0
#
# Explanation:
#
# fruits[0] = 3 is placed in baskets[0] = 6.
#
# fruits[1] = 6 cannot be placed in baskets[1] = 4 (insufficient capacity)
# but can be placed in the next available basket, baskets[2] = 7.
#
# fruits[2] = 1 is placed in baskets[1] = 4.
#
# Since all fruits are successfully placed, we return 0.
#
# Constraints:
#
# n == fruits.length == baskets.length
#
# 1 <= n <= 10^5
#
# 1 <= fruits[i], baskets[i] <= 10^9
#

# @lc code=start
from typing import List


class SegmentTree:
    """Max segment tree supporting leftmost query of value >= target."""

    def __init__(self, nums: List[int]) -> None:
        self.n = len(nums)
        self.tree = [0] * (4 * self.n)
        self._build(nums, 0, 0, self.n - 1)

    def _build(self, nums: List[int], idx: int, lo: int, hi: int) -> None:
        if lo == hi:
            self.tree[idx] = nums[lo]
            return
        mid = (lo + hi) // 2
        self._build(nums, 2 * idx + 1, lo, mid)
        self._build(nums, 2 * idx + 2, mid + 1, hi)
        self.tree[idx] = max(self.tree[2 * idx + 1], self.tree[2 * idx + 2])

    def update(self, i: int, val: int) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        self._update(0, 0, self.n - 1, i, val)

    def _update(self, idx: int, lo: int, hi: int, i: int, val: int) -> None:
        if lo == hi:
            self.tree[idx] = val
            return
        mid = (lo + hi) // 2
        if i <= mid:
            self._update(2 * idx + 1, lo, mid, i, val)
        else:
            self._update(2 * idx + 2, mid + 1, hi, i, val)
        self.tree[idx] = max(self.tree[2 * idx + 1], self.tree[2 * idx + 2])

    def query_first(self, target: int) -> int:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        return self._query_first(0, 0, self.n - 1, target)

    def _query_first(self, idx: int, lo: int, hi: int, target: int) -> int:
        if self.tree[idx] < target:
            return -1
        if lo == hi:
            self.update(lo, -1)
            return lo
        mid = (lo + hi) // 2
        if self.tree[2 * idx + 1] >= target:
            return self._query_first(2 * idx + 1, lo, mid, target)
        return self._query_first(2 * idx + 2, mid + 1, hi, target)


class Solution:
    def numOfUnplacedFruits(self, fruits: List[int], baskets: List[int]) -> int:
        """
        Interview explanation:
        Same placement rule as Fruits Into Baskets II but n <= 1e5, so use a
        max segment tree to find the leftmost basket >= fruit in O(log n).

        Algorithm:
        - Build max segtree on baskets.
        - For each fruit, query leftmost index with capacity >= fruit; mark used
          by setting that leaf to -1. Count failures.

        Complexity: O(n log n) time, O(n) space.
        """
        tree = SegmentTree(baskets)
        unplaced = 0
        for fruit in fruits:
            if tree.query_first(fruit) == -1:
                unplaced += 1
        return unplaced
# @lc code=end


