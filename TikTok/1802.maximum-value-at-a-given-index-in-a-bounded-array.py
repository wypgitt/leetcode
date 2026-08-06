#
# @lc app=leetcode id=1802 lang=python3
#
# [1802] Maximum Value at a Given Index in a Bounded Array
#
# https://leetcode.com/problems/maximum-value-at-a-given-index-in-a-bounded-array/description/
#
# algorithms
# Medium (38.83%)
# Likes:    2748
# Dislikes: 479
# Total Accepted:    90.7K
# Total Submissions: 234K
# Testcase Example:  "4"
#
# You are given three positive integers: n, index, and maxSum. You want to
# construct an array nums (0-indexed) that satisfies the following conditions:
#
# nums.length == n
#
# nums[i] is a positive integer where 0 <= i < n.
#
# abs(nums[i] - nums[i+1]) <= 1 where 0 <= i < n-1.
#
# The sum of all the elements of nums does not exceed maxSum.
#
# nums[index] is maximized.
#
# Return nums[index] of the constructed array.
#
# Note that abs(x) equals x if x >= 0, and -x otherwise.
#
# Example 1:
#
# Input: n = 4, index = 2, maxSum = 6
# Output: 2
# Explanation: nums = [1,2,2,1] is one array that satisfies all the conditions.
# There are no arrays that satisfy all the conditions and have nums[2] == 3, so
# 2 is the maximum nums[2].
#
# Example 2:
#
# Input: n = 6, index = 1, maxSum = 10
# Output: 3
#
# Constraints:
#
# 1 <= n <= maxSum <= 10^9
#
# 0 <= index < n
#

# @lc code=start
class Solution:
    def maxValue(self, n: int, index: int, maxSum: int) -> int:
        """
        Interview explanation:
        Maximize nums[index] under sum(nums)=maxSum, |a[i]-a[i+1]|<=1, positives.
        Peak at index slopes down by 1 each step (floor at 1). Binary search peak.

        Algorithm (binary search):
        - Check(mid): sum of left arm of length index and right of n-index-1
          with peak mid, each arm arithmetic to max(1,...).
        - Maximize mid in [1, maxSum].

        Complexity: O(log maxSum) time, O(1) space.
        """
        def arm(length: int, peak: int) -> int:
            if length == 0:
                return 0
            if peak > length:
                # peak-1 ... peak-length
                return (peak - 1 + peak - length) * length // 2
            # peak-1 ... 1, then 1's
            return (peak - 1) * peak // 2 + (length - (peak - 1))

        lo, hi = 1, maxSum
        ans = 1
        while lo <= hi:
            mid = (lo + hi) // 2
            total = arm(index, mid) + mid + arm(n - index - 1, mid)
            if total <= maxSum:
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
# @lc code=end
