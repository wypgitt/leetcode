#
# @lc app=leetcode id=2420 lang=python3
#
# [2420] Find All Good Indices
#
# https://leetcode.com/problems/find-all-good-indices/description/
#
# algorithms
# Medium (41.16%)
# Likes:    685
# Dislikes: 41
# Total Accepted:    33.6K
# Total Submissions: 81.7K
# Testcase Example:  "[2,1,1,1,3,4,1]\n2"
#
# You are given a 0-indexed integer array nums of size n and a positive integer
# k.
#
# We call an index i in the range k <= i < n - k good if the following
# conditions are satisfied:
#
#
# The k elements that are just before the index i are in non-increasing order.
#
#
# The k elements that are just after the index i are in non-decreasing order.
#
# Return an array of all good indices sorted in increasing order.
#
#
#
# Example 1:
#
# Input: nums = [2,1,1,1,3,4,1], k = 2
# Output: [2,3]
# Explanation: There are two good indices in the array:
# - Index 2. The subarray [2,1] is in non-increasing order, and the subarray
# [1,3] is in non-decreasing order.
# - Index 3. The subarray [1,1] is in non-increasing order, and the subarray
# [3,4] is in non-decreasing order.
# Note that the index 4 is not good because [4,1] is not non-decreasing.
#
# Example 2:
#
# Input: nums = [2,1,1,2], k = 2
# Output: []
# Explanation: There are no good indices in this array.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 3 <= n <= 10^5
#
#
# 1 <= nums[i] <= 10^6
#
#
# 1 <= k <= n / 2
#

# @lc code=start
from typing import List


class Solution:
    def goodIndices(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Index i is good if k elements before are non-increasing and k after are
        non-decreasing.

        Algorithm:
        - Pref: longest non-increasing streak ending at i; suff: non-decreasing
          starting at i; good if pref[i-1]>=k and suff[i+1]>=k.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        dec = [1] * n
        inc = [1] * n
        for i in range(1, n):
            if nums[i] <= nums[i - 1]:
                dec[i] = dec[i - 1] + 1
        for i in range(n - 2, -1, -1):
            if nums[i] <= nums[i + 1]:
                inc[i] = inc[i + 1] + 1
        return [i for i in range(k, n - k) if dec[i - 1] >= k and inc[i + 1] >= k]
# @lc code=end
