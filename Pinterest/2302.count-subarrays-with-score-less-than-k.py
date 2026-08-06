#
# @lc app=leetcode id=2302 lang=python3
#
# [2302] Count Subarrays With Score Less Than K
#
# https://leetcode.com/problems/count-subarrays-with-score-less-than-k/description/
#
# algorithms
# Hard (62.20%)
# Likes:    1646
# Dislikes: 63
# Total Accepted:    153.4K
# Total Submissions: 246.6K
# Testcase Example:  "[2,1,4,3,5]\n10"
#
# The score of an array is defined as the product of its sum and its length.
#
#
# For example, the score of [1, 2, 3, 4, 5] is (1 + 2 + 3 + 4 + 5) * 5 = 75.
#
# Given a positive integer array nums and an integer k, return the number of
# non-empty subarrays of nums whose score is strictly less than k.
#
# A subarray is a contiguous sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [2,1,4,3,5], k = 10
# Output: 6
# Explanation:
# The 6 subarrays having scores less than 10 are:
# - [2] with score 2 * 1 = 2.
# - [1] with score 1 * 1 = 1.
# - [4] with score 4 * 1 = 4.
# - [3] with score 3 * 1 = 3.
# - [5] with score 5 * 1 = 5.
# - [2,1] with score (2 + 1) * 2 = 6.
# Note that subarrays such as [1,4] and [4,3,5] are not considered because their
# scores are 10 and 36 respectively, while we need scores strictly less than 10.
#
# Example 2:
#
# Input: nums = [1,1,1], k = 5
# Output: 5
# Explanation:
# Every subarray except [1,1,1] has a score less than 5.
# [1,1,1] has a score (1 + 1 + 1) * 3 = 9, which is greater than 5.
# Thus, there are 5 subarrays having scores less than 5.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^5
#
#
# 1 <= k <= 10^15
#

# @lc code=start
from typing import List


class Solution:
    def countSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count contiguous subarrays whose score (sum * length) is strictly < k.

        Algorithm:
        - Sliding window: expand right, shrink left while sum*(r-l+1) >= k.
        - Each right endpoint contributes (r-l+1) valid subarrays ending at r.

        Complexity: O(n) time, O(1) space.
        """
        ans = cur = left = 0
        for right, x in enumerate(nums):
            cur += x
            while left <= right and cur * (right - left + 1) >= k:
                cur -= nums[left]
                left += 1
            ans += right - left + 1
        return ans

    def countSubarrays_two_pointers(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Same two-pointers window; alternate naming for interview clarity.

        Algorithm:
        - Maintain prefix sum of the window; shrink when score >= k.

        Complexity: O(n) time, O(1) space.
        """
        return self.countSubarrays(nums, k)
# @lc code=end
