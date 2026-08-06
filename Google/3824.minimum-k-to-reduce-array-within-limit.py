#
# @lc app=leetcode id=3824 lang=python3
#
# [3824] Minimum K to Reduce Array Within Limit
#
# https://leetcode.com/problems/minimum-k-to-reduce-array-within-limit/description/
#
# algorithms
# Medium (41.02%)
# Likes:    70
# Dislikes: 4
# Total Accepted:    48.1K
# Total Submissions: 117.3K
# Testcase Example:  "[3,7,5]"
#
#
# You are given a positive integer array nums.
#
# For a positive integer k, define nonPositive(nums, k) as the minimum
# number of operations needed to make every element of nums non-positive.
# In one operation, you can choose an index i and reduce nums[i] by k.
#
# Return an integer denoting the minimum value of k such that
# nonPositive(nums, k) <= k^2.
#
# Example 1:
#
# Input: nums = [3,7,5]
#
# Output: 3
#
# Explanation:
#
# When k = 3, nonPositive(nums, k) = 6 <= k^2.
#
# Reduce nums[0] = 3 one time. nums[0] becomes 3 - 3 = 0.
#
# Reduce nums[1] = 7 three times. nums[1] becomes 7 - 3 - 3 - 3 = -2.
#
# Reduce nums[2] = 5 two times. nums[2] becomes 5 - 3 - 3 = -1.
#
# Example 2:
#
# Input: nums = [1]
#
# Output: 1
#
# Explanation:
#
# When k = 1, nonPositive(nums, k) = 1 <= k^2.
#
# Reduce nums[0] = 1 one time. nums[0] becomes 1 - 1 = 0.
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
    def minimumK(self, nums: List[int]) -> int:
        """
        Interview explanation:
        nonPositive(nums, k) = sum ceil(x/k). Need the least k > 0 with
        that sum <= k^2. Larger k only helps, so binary search.

        Algorithm:
        - Binary search k in [1, 1e5]; check sum((x+k-1)//k) <= k*k.

        Complexity: O(n log M) time, O(1) space.
        """
        def check(k: int) -> bool:
            t = 0
            for x in nums:
                t += (x + k - 1) // k
            return t <= k * k

        l, r = 1, 10**5
        while l < r:
            mid = (l + r) >> 1
            if check(mid):
                r = mid
            else:
                l = mid + 1
        return l
# @lc code=end
