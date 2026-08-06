#
# @lc app=leetcode id=3422 lang=python3
#
# [3422] Minimum Operations to Make Subarray Elements Equal
#
# https://leetcode.com/problems/minimum-operations-to-make-subarray-elements-equal/description/
#
# algorithms
# Medium (46.42%)
# Likes:    9
# Dislikes: 5
# Total Accepted:    766
# Total Submissions: 1.6K
# Testcase Example:  "[4,-3,2,1,-4,6]\n3"
#
#
# You are given an integer array nums and an integer k. You can perform
# the following operation any number of times:
#
# Increase or decrease any element of nums by 1.
#
# Return the minimum number of operations required to ensure that at least
# one subarray of size k in nums has all elements equal.
#
# Example 1:
#
# Input: nums = [4,-3,2,1,-4,6], k = 3
#
# Output: 5
#
# Explanation:
#
# Use 4 operations to add 4 to nums[1]. The resulting array is [4, 1, 2,
# 1, -4, 6].
#
# Use 1 operation to subtract 1 from nums[2]. The resulting array is [4,
# 1, 1, 1, -4, 6].
#
# The array now contains a subarray [1, 1, 1] of size k = 3 with all
# elements equal. Hence, the answer is 5.
#
# Example 2:
#
# Input: nums = [-2,-2,3,1,4], k = 2
#
# Output: 0
#
# Explanation:
#
# The subarray [-2, -2] of size k = 2 already contains all equal elements,
# so no operations are needed. Hence, the answer is 0.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# -10^6 <= nums[i] <= 10^6
#
# 2 <= k <= nums.length
#

# @lc code=start
from typing import List

from sortedcontainers import SortedList


class Solution:
    def minOperations(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        For a window of size k, the cheapest target is the median (minimizes L1
        distance). Slide every window of length k and take the minimum median-cost.

        Algorithm:
        - Maintain two SortedLists of (value, index): left = smaller half, right =
          larger half (median = min of right). Track half-sums for O(1) cost.
        - On insert: push to left, move max to right, rebalance sizes.
        - Cost = (right_sum - med*|right|) + (med*|left| - left_sum).

        Complexity: O(n log k) time, O(k) space.
        """
        left: SortedList = SortedList()
        right: SortedList = SortedList()
        s1 = s2 = 0
        ans = 10**30
        for i, x in enumerate(nums):
            left.add((x, i))
            s1 += x
            y, yi = left.pop()
            s1 -= y
            right.add((y, yi))
            s2 += y
            if len(right) - len(left) > 1:
                y, yi = right.pop(0)
                s2 -= y
                left.add((y, yi))
                s1 += y
            if i >= k - 1:
                med = right[0][0]
                ans = min(ans, s2 - med * len(right) + med * len(left) - s1)
                j = i - k + 1
                rem = (nums[j], j)
                if rem in right:
                    right.remove(rem)
                    s2 -= nums[j]
                else:
                    left.remove(rem)
                    s1 -= nums[j]
        return ans
# @lc code=end
