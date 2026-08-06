#
# @lc app=leetcode id=3721 lang=python3
#
# [3721] Longest Balanced Subarray II
#
# https://leetcode.com/problems/longest-balanced-subarray-ii/description/
#
# algorithms
# Hard (33.80%)
# Likes:    360
# Dislikes: 65
# Total Accepted:    61.6K
# Total Submissions: 182.2K
# Testcase Example:  "[2,5,4,3]"
#
#
# You are given an integer array nums.
#
# A subarray is called balanced if the number of distinct even numbers in
# the subarray is equal to the number of distinct odd numbers.
#
# Return the length of the longest balanced subarray.
#
# Example 1:
#
# Input: nums = [2,5,4,3]
#
# Output: 4
#
# Explanation:
#
# The longest balanced subarray is [2, 5, 4, 3].
#
# It has 2 distinct even numbers [2, 4] and 2 distinct odd numbers [5, 3].
# Thus, the answer is 4.
#
# Example 2:
#
# Input: nums = [3,2,2,5,4]
#
# Output: 5
#
# Explanation:
#
# The longest balanced subarray is [3, 2, 2, 5, 4].
#
# It has 2 distinct even numbers [2, 4] and 2 distinct odd numbers [3, 5].
# Thus, the answer is 5.
#
# Example 3:
#
# Input: nums = [1,2,3,2]
#
# Output: 3
#
# Explanation:
#
# The longest balanced subarray is [2, 3, 2].
#
# It has 1 distinct even number [2] and 1 distinct odd number [3]. Thus,
# the answer is 3.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def longestBalanced(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Map each distinct odd to +1 and distinct even to -1. For right endpoint i,
        find the leftmost cut j with the same distinct-vote sum using a segment
        tree over last-occurrence suffix contributions.

        Algorithm:
        - Segment tree on indices [0..n] with range add and find-first equal.
        - last[x] = latest index of x; now = distinct vote sum of the prefix.
        - On seeing x: remove old suffix contrib if any, set last[x]=i, add new
          suffix; query earliest pos with value == now; ans = max(i - pos).

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)

        class Node:
            __slots__ = ("l", "r", "mn", "mx", "lazy")

            def __init__(self):
                self.l = self.r = 0
                self.mn = self.mx = 0
                self.lazy = 0

        tr = [Node() for _ in range((n + 1) * 4)]

        def build(u: int, l: int, r: int) -> None:
            tr[u].l, tr[u].r = l, r
            tr[u].mn = tr[u].mx = tr[u].lazy = 0
            if l == r:
                return
            mid = (l + r) >> 1
            build(u << 1, l, mid)
            build(u << 1 | 1, mid + 1, r)

        def apply(u: int, v: int) -> None:
            tr[u].mn += v
            tr[u].mx += v
            tr[u].lazy += v

        def pushdown(u: int) -> None:
            if tr[u].lazy:
                apply(u << 1, tr[u].lazy)
                apply(u << 1 | 1, tr[u].lazy)
                tr[u].lazy = 0

        def pushup(u: int) -> None:
            tr[u].mn = min(tr[u << 1].mn, tr[u << 1 | 1].mn)
            tr[u].mx = max(tr[u << 1].mx, tr[u << 1 | 1].mx)

        def modify(u: int, l: int, r: int, v: int) -> None:
            if tr[u].l >= l and tr[u].r <= r:
                apply(u, v)
                return
            pushdown(u)
            mid = (tr[u].l + tr[u].r) >> 1
            if l <= mid:
                modify(u << 1, l, r, v)
            if r > mid:
                modify(u << 1 | 1, l, r, v)
            pushup(u)

        def query(u: int, target: int) -> int:
            if tr[u].l == tr[u].r:
                return tr[u].l
            pushdown(u)
            if tr[u << 1].mn <= target <= tr[u << 1].mx:
                return query(u << 1, target)
            return query(u << 1 | 1, target)

        build(1, 0, n)
        last = {}
        now = ans = 0

        for i, x in enumerate(nums, start=1):
            det = 1 if (x & 1) else -1
            if x in last:
                modify(1, last[x], n, -det)
                now -= det
            last[x] = i
            modify(1, i, n, det)
            now += det
            pos = query(1, now)
            ans = max(ans, i - pos)

        return ans
# @lc code=end
