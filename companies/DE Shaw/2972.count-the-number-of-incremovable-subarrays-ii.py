#
# @lc app=leetcode id=2972 lang=python3
#
# [2972] Count the Number of Incremovable Subarrays II
#
# https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-ii/description/
#
# algorithms
# Hard (40.69%)
# Likes:    246
# Dislikes: 20
# Total Accepted:    11.8K
# Total Submissions: 29.1K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given a 0-indexed array of positive integers nums.
#
# A subarray of nums is called incremovable if nums becomes strictly
# increasing on removing the subarray. For example, the subarray [3, 4] is
# an incremovable subarray of [5, 3, 4, 6, 7] because removing this
# subarray changes the array [5, 3, 4, 6, 7] to [5, 6, 7] which is
# strictly increasing.
#
# Return the total number of incremovable subarrays of nums.
#
# Note that an empty array is considered strictly increasing.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: 10
# Explanation: The 10 incremovable subarrays are: [1], [2], [3], [4],
# [1,2], [2,3], [3,4], [1,2,3], [2,3,4], and [1,2,3,4], because on
# removing any one of these subarrays nums becomes strictly increasing.
# Note that you cannot select an empty subarray.
#
# Example 2:
#
# Input: nums = [6,5,7,8]
# Output: 7
# Explanation: The 7 incremovable subarrays are: [5], [6], [5,7], [6,5],
# [5,7,8], [6,5,7] and [6,5,7,8].
# It can be shown that there are only 7 incremovable subarrays in nums.
#
# Example 3:
#
# Input: nums = [8,7,6,6]
# Output: 3
# Explanation: The 3 incremovable subarrays are: [8,7,6], [7,6,6], and
# [8,7,6,6]. Note that [8,7] is not an incremovable subarray because after
# removing [8,7] nums becomes [6,6], which is sorted in ascending order
# but not strictly increasing.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def incremovableSubarrayCount(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same as 2970 but n <= 1e5: remaining parts must be a prefix of the longest
        strictly-increasing prefix and a suffix of the longest strictly-increasing suffix.

        Algorithm:
        - Find prefix end i and suffix start j. If the whole array is increasing, return
          n(n+1)/2. Else count (empty left + prefixes) joined with each suffix start via
          two pointers on nums[k] < nums[j2].

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        i = 0
        while i + 1 < n and nums[i] < nums[i + 1]:
            i += 1
        if i == n - 1:
            return n * (n + 1) // 2
        ans = i + 2
        j = n - 1
        while j and nums[j - 1] < nums[j]:
            j -= 1
        k = 0
        for j2 in range(j, n):
            while k <= i and nums[k] < nums[j2]:
                k += 1
            ans += k + 1
        return ans
# @lc code=end
