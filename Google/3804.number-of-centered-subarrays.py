#
# @lc app=leetcode id=3804 lang=python3
#
# [3804] Number of Centered Subarrays
#
# https://leetcode.com/problems/number-of-centered-subarrays/description/
#
# algorithms
# Medium (67.40%)
# Likes:    78
# Dislikes: 3
# Total Accepted:    39.5K
# Total Submissions: 58.5K
# Testcase Example:  "[-1,1,0]"
#
#
# You are given an integer array nums.
#
# A subarray of nums is called centered if the sum of its elements is
# equal to at least one element within that same subarray.
#
# Return the number of centered subarrays of nums.
#
# Example 1:
#
# Input: nums = [-1,1,0]
#
# Output: 5
#
# Explanation:
#
# All single-element subarrays ([-1], [1], [0]) are centered.
#
# The subarray [1, 0] has a sum of 1, which is present in the subarray.
#
# The subarray [-1, 1, 0] has a sum of 0, which is present in the
# subarray.
#
# Thus, the answer is 5.
#
# Example 2:
#
# Input: nums = [2,-3]
#
# Output: 2
#
# Explanation:
#
# Only single-element subarrays ([2], [-3]) are centered.
#
# Constraints:
#
# 1 <= nums.length <= 500
#
# -10^5 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def centeredSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A subarray is centered if its sum appears as some element inside it.
        With n <= 500, enumerate all subarrays.

        Algorithm:
        - For each left endpoint i, grow right j while maintaining sum and a
          set of values in nums[i..j]; count when sum is in the set.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            st = set()
            s = 0
            for j in range(i, n):
                s += nums[j]
                st.add(nums[j])
                if s in st:
                    ans += 1
        return ans
# @lc code=end
