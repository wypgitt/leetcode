#
# @lc app=leetcode id=3224 lang=python3
#
# [3224] Minimum Array Changes to Make Differences Equal
#
# https://leetcode.com/problems/minimum-array-changes-to-make-differences-equal/description/
#
# algorithms
# Medium (24.90%)
# Likes:    263
# Dislikes: 28
# Total Accepted:    16K
# Total Submissions: 64.2K
# Testcase Example:  "[1,0,1,2,4,3]\n4"
#
#
# You are given an integer array nums of size n where n is even, and an
# integer k.
#
# You can perform some changes on the array, where in one change you can
# replace any element in the array with any integer in the range from 0 to
# k.
#
# You need to perform some changes (possibly none) such that the final
# array satisfies the following condition:
#
# There exists an integer X such that abs(a[i] - a[n - i - 1]) = X for all
# (0 <= i < n).
#
# Return the minimum number of changes required to satisfy the above
# condition.
#
# Example 1:
#
# Input: nums = [1,0,1,2,4,3], k = 4
#
# Output: 2
#
# Explanation:
#
# We can perform the following changes:
#
# Replace nums[1] by 2. The resulting array is nums = [1,2,1,2,4,3].
#
# Replace nums[3] by 3. The resulting array is nums = [1,2,1,3,4,3].
#
# The integer X will be 2.
#
# Example 2:
#
# Input: nums = [0,1,2,3,3,6,5,4], k = 6
#
# Output: 2
#
# Explanation:
#
# We can perform the following operations:
#
# Replace nums[3] by 0. The resulting array is nums = [0,1,2,0,3,6,5,4].
#
# Replace nums[4] by 4. The resulting array is nums = [0,1,2,0,4,6,5,4].
#
# The integer X will be 4.
#
# Constraints:
#
# 2 <= n == nums.length <= 10^5
#
# n is even.
#
# 0 <= nums[i] <= k <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minChanges(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Pair ends (nums[i], nums[n-1-i]). Choose a common difference X in [0, k]
        minimizing changes. Per pair, cost is 0/1/2 depending on current diff and
        the one-change reach limit.

        Algorithm:
        - For pair (a, b): d = |a-b|, limit = max(a, b, k-a, k-b).
          X == d -> 0; X <= limit -> 1; else 2.
        - Difference array over X in [0, k]: start from 2 per pair, subtract 1 on
          [0, limit], subtract 1 more at d; take the minimum prefix sum.

        Complexity: O(n + k) time, O(k) space.
        Alternate: count frequency of each d and sweep candidate X.
        """
        n = len(nums)
        pairs = n // 2
        diff = [0] * (k + 2)
        for i in range(pairs):
            a, b = nums[i], nums[n - 1 - i]
            d = abs(a - b)
            limit = max(a, b, k - a, k - b)
            diff[0] -= 1
            diff[limit + 1] += 1
            diff[d] -= 1
            diff[d + 1] += 1

        cur = 2 * pairs
        ans = cur
        for x in range(k + 1):
            cur += diff[x]
            ans = min(ans, cur)
        return ans

# @lc code=end
