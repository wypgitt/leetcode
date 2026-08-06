#
# @lc app=leetcode id=3073 lang=python3
#
# [3073] Maximum Increasing Triplet Value
#
# https://leetcode.com/problems/maximum-increasing-triplet-value/description/
#
# algorithms
# Medium (35.96%)
# Likes:    22
# Dislikes: 8
# Total Accepted:    1.4K
# Total Submissions: 4K
# Testcase Example:  "[5,6,9]"
#
#
# Given an array nums, return the maximum value of a triplet (i, j, k)
# such that i < j < k and nums[i] < nums[j] < nums[k].
#
# The value of a triplet (i, j, k) is nums[i] - nums[j] + nums[k].
#
# Example 1:
#
# Input:  nums = [5,6,9]
#
# Output:  8
#
# Explanation:  We only have one choice for an increasing triplet and that
# is choosing all three elements. The value of this triplet would be 5 - 6
# + 9 = 8.
#
# Example 2:
#
# Input:  nums = [1,5,3,6]
#
# Output:  4
#
# Explanation:  There are only two increasing triplets:
#
# (0, 1, 3): The value of this triplet is nums[0] - nums[1] + nums[3] = 1
# - 5 + 6 = 2.
#
# (0, 2, 3): The value of this triplet is nums[0] - nums[2] + nums[3] = 1
# - 3 + 6 = 4.
#
# Thus the answer would be 4.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# The input is generated such that at least one triplet meets the given
# condition.
#

# @lc code=start
from typing import List


class Solution:
    def maximumTripletValue(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize nums[i]-nums[j]+nums[k] under i<j<k and strictly increasing
        values. For each j, take max left value < nums[j] and the suffix max
        to the right when it exceeds nums[j].

        Algorithm:
        - Precompute suffix maxima. Fenwick max-tree on compressed ranks holds
          left values; query max among ranks < rank(nums[j]).

        Complexity: O(n log n) time, O(n) space.
        """
        class BIT:
            def __init__(self, n: int):
                self.n = n
                self.t = [0] * (n + 1)

            def update(self, i: int, v: int) -> None:
                while i <= self.n:
                    self.t[i] = max(self.t[i], v)
                    i += i & -i

            def query(self, i: int) -> int:
                res = 0
                while i > 0:
                    res = max(res, self.t[i])
                    i -= i & -i
                return res

        n = len(nums)
        vals = sorted(set(nums))
        rank = {v: i + 1 for i, v in enumerate(vals)}
        right = [0] * n
        right[-1] = nums[-1]
        for i in range(n - 2, -1, -1):
            right[i] = max(right[i + 1], nums[i])
        bit = BIT(len(vals))
        ans = float("-inf")
        for j in range(n - 1):
            if j >= 1 and right[j + 1] > nums[j]:
                mx = bit.query(rank[nums[j]] - 1)
                if mx:
                    ans = max(ans, mx - nums[j] + right[j + 1])
            bit.update(rank[nums[j]], nums[j])
        return int(ans)

    def maximumTripletValue_sortedlist(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: maintain a SortedList of left values and bisect for the
        largest strictly smaller than nums[j].

        Algorithm:
        - Same suffix-max idea; SortedList.bisect_left for left max.

        Complexity: O(n log n) time, O(n) space.
        """
        try:
            from sortedcontainers import SortedList
        except ImportError:
            return self.maximumTripletValue(nums)

        n = len(nums)
        right = [0] * n
        right[-1] = nums[-1]
        for i in range(n - 2, -1, -1):
            right[i] = max(right[i + 1], nums[i])
        left = SortedList()
        ans = float("-inf")
        for j in range(n - 1):
            if j >= 1 and right[j + 1] > nums[j]:
                idx = left.bisect_left(nums[j])
                if idx > 0:
                    ans = max(ans, left[idx - 1] - nums[j] + right[j + 1])
            left.add(nums[j])
        return int(ans)
# @lc code=end
