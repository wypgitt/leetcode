#
# @lc app=leetcode id=3915 lang=python3
#
# [3915] Maximum Sum of Alternating Subsequence With Distance at Least K
#
# https://leetcode.com/problems/maximum-sum-of-alternating-subsequence-with-distance-at-least-k/description/
#
# algorithms
# Hard (32.33%)
# Likes:    26
# Dislikes: 4
# Total Accepted:    4.6K
# Total Submissions: 14.1K
# Testcase Example:  "[5,4,2]\n2"
#
#
# You are given an integer array nums of length n and an integer k.
#
# Pick a subsequence with indices 0 <= i_1 < i_2 < ... < i_m < n such
# that:
#
# For every 1 <= t < m, i_t+1 - i_t >= k.
#
# The selected values form a strictly alternating sequence. In other
# words, either:
#
# nums[i_1] < nums[i_2] > nums[i_3] < ..., or
#
# nums[i_1] > nums[i_2] < nums[i_3] > ...
#
# A subsequence of length 1 is also considered strictly alternating. The
# score of a valid subsequence is the sum of its selected values.
#
# Return an integer denoting the maximum possible score of a valid
# subsequence.
#
# Example 1:
#
# Input: nums = [5,4,2], k = 2
#
# Output: 7
#
# Explanation:
#
# An optimal choice is indices [0, 2], which gives values [5, 2].
#
# The distance condition holds because 2 - 0 = 2 >= k.
#
# The values are strictly alternating because 5 > 2.
#
# The score is 5 + 2 = 7.
#
# Example 2:
#
# Input: nums = [3,5,4,2,4], k = 1
#
# Output: 14
#
# Explanation:
#
# An optimal choice is indices [0, 1, 3, 4], which gives values [3, 5, 2,
# 4].
#
# The distance condition holds because each pair of consecutive chosen
# indices differs by at least k = 1.
#
# The values are strictly alternating since 3 < 5 > 2 < 4.
#
# The score is 3 + 5 + 2 + 4 = 14.
#
# Example 3:
#
# Input: nums = [5], k = 1
#
# Output: 5
#
# Explanation:
#
# The only valid subsequence is [5]. A subsequence with 1 element is
# always strictly alternating, so the score is 5.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= n
#

# @lc code=start
from typing import List


class SegTreeMax:
    __slots__ = ("n", "size", "neg", "t")

    def __init__(self, n: int, neg: int = -(10**18)) -> None:
        """
        Interview explanation:
        Iterative max segment tree: point max-assign updates, range max queries.

        Algorithm:
        - Pad to power of two; leaves hold values, parents store max of children.

        Complexity: O(n) build time/space.
        """
        self.n = n
        self.neg = neg
        size = 1
        while size < n:
            size <<= 1
        self.size = size
        self.t = [neg] * (2 * size)

    def update(self, i: int, val: int) -> None:
        """
        Interview explanation:
        Point update: set leaf to max(current, val) and refresh ancestors.

        Algorithm:
        - Write leaf, walk up combining sibling maxes.

        Complexity: O(log n) time, O(1) space.
        """
        i += self.size
        self.t[i] = max(self.t[i], val)
        i >>= 1
        while i:
            self.t[i] = max(self.t[2 * i], self.t[2 * i + 1])
            i >>= 1

    def query(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Range maximum on inclusive [l, r]; empty/invalid ranges return neg.

        Algorithm:
        - Clamp bounds; iterative pull of odd/even segment nodes.

        Complexity: O(log n) time, O(1) space.
        """
        if l > r or l < 0 or r >= self.n:
            if l > r:
                return self.neg
            l = max(l, 0)
            r = min(r, self.n - 1)
            if l > r:
                return self.neg
        l += self.size
        r += self.size
        res = self.neg
        while l <= r:
            if l & 1:
                res = max(res, self.t[l])
                l += 1
            if not (r & 1):
                res = max(res, self.t[r])
                r -= 1
            l >>= 1
            r >>= 1
        return res


class Solution:
    def maxAlternatingSum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Max sum of a strictly alternating subsequence (<>< or ><>) with
        consecutive indices at least k apart.

        Algorithm:
        - high[i]/low[i]: best ending at i as a local high / local low.
        - Compress values; keep two max segtrees of endings that are already
          index-eligible (lagged by k).
        - Extend: attach nums[i] after a smaller low or a larger high.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        vals = sorted(set(nums))
        coord = {v: i for i, v in enumerate(vals)}
        m = len(vals)
        neg = -(10**18)

        st_low = SegTreeMax(m, neg)
        st_high = SegTreeMax(m, neg)

        high = [neg] * n
        low = [neg] * n
        ans = neg

        for i in range(n):
            if i >= k:
                p = i - k
                st_low.update(coord[nums[p]], low[p])
                st_high.update(coord[nums[p]], high[p])

            pos = coord[nums[i]]
            ml = st_low.query(0, pos - 1)
            mh = st_high.query(pos + 1, m - 1)

            high[i] = nums[i]
            low[i] = nums[i]
            if ml != neg:
                high[i] = max(high[i], ml + nums[i])
            if mh != neg:
                low[i] = max(low[i], mh + nums[i])

            ans = max(ans, high[i], low[i])

        return ans
# @lc code=end
