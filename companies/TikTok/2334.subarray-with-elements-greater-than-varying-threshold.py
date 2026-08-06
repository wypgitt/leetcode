#
# @lc app=leetcode id=2334 lang=python3
#
# [2334] Subarray With Elements Greater Than Varying Threshold
#
# https://leetcode.com/problems/subarray-with-elements-greater-than-varying-threshold/description/
#
# algorithms
# Hard (45.78%)
# Likes:    618
# Dislikes: 11
# Total Accepted:    18.7K
# Total Submissions: 40.8K
# Testcase Example:  "[1,3,4,3,1]\n6"
#
# You are given an integer array nums and an integer threshold.
#
# Find any subarray of nums of length k such that every element in the subarray
# is greater than threshold / k.
#
# Return the size of any such subarray. If there is no such subarray, return -1.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [1,3,4,3,1], threshold = 6
# Output: 3
# Explanation: The subarray [3,4,3] has a size of 3, and every element is
# greater than 6 / 3 = 2.
# Note that this is the only valid subarray.
#
# Example 2:
#
# Input: nums = [6,5,6,5,8], threshold = 7
# Output: 1
# Explanation: The subarray [8] has a size of 1, and 8 > 7 / 1 = 7. So 1 is
# returned.
# Note that the subarray [6,5] has a size of 2, and every element is greater
# than 7 / 2 = 3.5.
# Similarly, the subarrays [6,5,6], [6,5,6,5], [6,5,6,5,8] also satisfy the
# given conditions.
# Therefore, 2, 3, 4, or 5 may also be returned.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i], threshold <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def validSubarraySize(self, nums: List[int], threshold: int) -> int:
        """
        Interview explanation:
        Find any subarray where every element > threshold / length; return its
        length (any), or -1.

        Algorithm:
        - Equivalent: for length k, need min(subarray) > threshold/k, i.e.
          min * k > threshold. Use next smaller element (monotone stack) to get
          the largest window where nums[i] is the minimum; check
          nums[i] * window > threshold.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        left = [-1] * n  # previous strictly smaller
        right = [n] * n  # next strictly smaller
        st = []
        for i, x in enumerate(nums):
            while st and nums[st[-1]] >= x:
                st.pop()
            left[i] = st[-1] if st else -1
            st.append(i)
        st.clear()
        for i in range(n - 1, -1, -1):
            while st and nums[st[-1]] >= nums[i]:
                st.pop()
            right[i] = st[-1] if st else n
            st.append(i)
        for i, x in enumerate(nums):
            k = right[i] - left[i] - 1
            if x * k > threshold:
                return k
        return -1
# @lc code=end
