#
# @lc app=leetcode id=3318 lang=python3
#
# [3318] Find X-Sum of All K-Long Subarrays I
#
# https://leetcode.com/problems/find-x-sum-of-all-k-long-subarrays-i/description/
#
# algorithms
# Easy (76.08%)
# Likes:    572
# Dislikes: 330
# Total Accepted:    145.6K
# Total Submissions: 191.3K
# Testcase Example:  "[1,1,2,2,3,4,2,3]\n6\n2"
#
#
# You are given an array nums of n integers and two integers k and x.
#
# The x-sum of an array is calculated by the following procedure:
#
# Count the occurrences of all elements in the array.
#
# Keep only the occurrences of the top x most frequent elements. If two
# elements have the same number of occurrences, the element with the
# bigger value is considered more frequent.
#
# Calculate the sum of the resulting array.
#
# Note that if an array has less than x distinct elements, its x-sum is
# the sum of the array.
#
# Return an integer array answer of length n - k + 1 where answer[i] is
# the x-sum of the subarray nums[i..i + k - 1].
#
# Example 1:
#
# Input: nums = [1,1,2,2,3,4,2,3], k = 6, x = 2
#
# Output: [6,10,12]
#
# Explanation:
#
# For subarray [1, 1, 2, 2, 3, 4], only elements 1 and 2 will be kept in
# the resulting array. Hence, answer[0] = 1 + 1 + 2 + 2.
#
# For subarray [1, 2, 2, 3, 4, 2], only elements 2 and 4 will be kept in
# the resulting array. Hence, answer[1] = 2 + 2 + 2 + 4. Note that 4 is
# kept in the array since it is bigger than 3 and 1 which occur the same
# number of times.
#
# For subarray [2, 2, 3, 4, 2, 3], only elements 2 and 3 are kept in the
# resulting array. Hence, answer[2] = 2 + 2 + 2 + 3 + 3.
#
# Example 2:
#
# Input: nums = [3,8,7,8,7,5], k = 2, x = 2
#
# Output: [11,15,15,15,12]
#
# Explanation:
#
# Since k == x, answer[i] is equal to the sum of the subarray nums[i..i +
# k - 1].
#
# Constraints:
#
# 1 <= n == nums.length <= 50
#
# 1 <= nums[i] <= 50
#
# 1 <= x <= k <= nums.length
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def findXSum(self, nums: List[int], k: int, x: int) -> List[int]:
        """
        Interview explanation:
        For each window of length k, keep the top x most frequent values
        (tie-break by larger value) and sum their occurrences in the window.

        Algorithm:
        - Slide windows; Counter frequencies; sort keys by (-freq, -value);
          sum freq*val for the top x.

        Complexity: O((n-k+1) * U log U) with U distinct <= 50, O(U) space.
        """
        n = len(nums)
        ans = []
        for i in range(n - k + 1):
            cnt = Counter(nums[i : i + k])
            top = sorted(cnt.items(), key=lambda p: (p[1], p[0]), reverse=True)[:x]
            ans.append(sum(val * freq for val, freq in top))
        return ans
# @lc code=end
