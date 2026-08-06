#
# @lc app=leetcode id=644 lang=python3
#
# [644] Maximum Average Subarray II
#
# https://leetcode.com/problems/maximum-average-subarray-ii/description/
#
# algorithms
# Hard (37.84%)
# Likes:    641
# Dislikes: 74
# Total Accepted:    23.3K
# Total Submissions: 61.6K
# Testcase Example:  "[1,12,-5,-6,50,3]\n4"
#
#
# You are given an integer array nums consisting of n elements, and an
# integer k.
#
# Find a contiguous subarray whose length is greater than or equal to k
# that has the maximum average value and return this value. Any answer
# with a calculation error less than 10^-5 will be accepted.
#
# Example 1:
#
# Input: nums = [1,12,-5,-6,50,3], k = 4
# Output: 12.75000
# Explanation:
# - When the length is 4, averages are [0.5, 12.75, 10.5] and the maximum
# average is 12.75
# - When the length is 5, averages are [10.4, 10.8] and the maximum
# average is 10.8
# - When the length is 6, averages are [9.16667] and the maximum average
# is 9.16667
# The maximum average is when we choose a subarray of length 4 (i.e., the
# sub array [12, -5, -6, 50]) which has the max average 12.75, so we
# return 12.75
# Note that we do not consider the subarrays of length < 4.
#
# Example 2:
#
# Input: nums = [5], k = 1
# Output: 5.00000
#
# Constraints:
#
# n == nums.length
#
# 1 <= k <= n <= 10^4
#
# -10^4 <= nums[i] <= 10^4
#
# @lc code=start

from typing import List


class Solution:
    def findMaxAverage(self, nums: List[int], k: int) -> float:
        """
        Interview explanation:
        Premium. Max average of any subarray with length >= k. Binary search the
        average x; check if some subarray length >= k has average >= x via
        transformed prefix sums (nums[i]-x).

        Algorithm:
        - Binary search mid in [min(nums), max(nums)].
        - check(x): a[i]=nums[i]-x; if some window len>=k has sum>=0 using
          prefix and min prefix before i-k+1.
        - Precision ~1e-5.

        Complexity: O(N log R) time, O(N) space for prefixes.
        """
        def check(x: float) -> bool:
            n = len(nums)
            prefix = [0.0] * (n + 1)
            for i in range(n):
                prefix[i + 1] = prefix[i] + nums[i] - x
            min_prefix = 0.0
            for i in range(k, n + 1):
                if prefix[i] - min_prefix >= 0:
                    return True
                min_prefix = min(min_prefix, prefix[i - k + 1])
            return False

        lo, hi = min(nums), max(nums)
        for _ in range(80):
            mid = (lo + hi) / 2
            if check(mid):
                lo = mid
            else:
                hi = mid
        return lo
# @lc code=end
