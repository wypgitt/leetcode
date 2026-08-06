#
# @lc app=leetcode id=3364 lang=python3
#
# [3364] Minimum Positive Sum Subarray 
#
# https://leetcode.com/problems/minimum-positive-sum-subarray/description/
#
# algorithms
# Easy (45.49%)
# Likes:    176
# Dislikes: 39
# Total Accepted:    50.4K
# Total Submissions: 110.8K
# Testcase Example:  "[3,-2,1,4]\n2\n3"
#
#
# You are given an integer array nums and two integers l and r. Your task
# is to find the minimum sum of a subarray whose size is between l and r
# (inclusive) and whose sum is greater than 0.
#
# Return the minimum sum of such a subarray. If no such subarray exists,
# return -1.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [3, -2, 1, 4], l = 2, r = 3
#
# Output: 1
#
# Explanation:
#
# The subarrays of length between l = 2 and r = 3 where the sum is greater
# than 0 are:
#
# [3, -2] with a sum of 1
#
# [1, 4] with a sum of 5
#
# [3, -2, 1] with a sum of 2
#
# [-2, 1, 4] with a sum of 3
#
# Out of these, the subarray [3, -2] has a sum of 1, which is the smallest
# positive sum. Hence, the answer is 1.
#
# Example 2:
#
# Input: nums = [-2, 2, -3, 1], l = 2, r = 3
#
# Output: -1
#
# Explanation:
#
# There is no subarray of length between l and r that has a sum greater
# than 0. So, the answer is -1.
#
# Example 3:
#
# Input: nums = [1, 2, 3, 4], l = 2, r = 4
#
# Output: 3
#
# Explanation:
#
# The subarray [1, 2] has a length of 2 and the minimum sum greater than
# 0. So, the answer is 3.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= l <= r <= nums.length
#
# -1000 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def minimumSumSubarray(self, nums: List[int], l: int, r: int) -> int:
        """
        Interview explanation:
        Find the smallest positive subarray sum among lengths in [l, r].
        n <= 100, so enumerate all windows.

        Algorithm:
        - Prefix sums; for each length in [l,r] and each start, take positive sums.
        - Track the minimum; return -1 if none.

        Complexity: O(n * (r - l + 1)) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x
        ans = 10**18
        for length in range(l, r + 1):
            for i in range(n - length + 1):
                s = pref[i + length] - pref[i]
                if s > 0:
                    ans = min(ans, s)
        return ans if ans < 10**18 else -1

    def minimumSumSubarray_brute(self, nums: List[int], l: int, r: int) -> int:
        """
        Interview explanation:
        Alternate: running window sum without prefix array.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(nums)
        ans = 10**18
        for i in range(n):
            s = 0
            for j in range(i, n):
                s += nums[j]
                length = j - i + 1
                if l <= length <= r and s > 0:
                    ans = min(ans, s)
        return ans if ans < 10**18 else -1
# @lc code=end
