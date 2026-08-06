#
# @lc app=leetcode id=2012 lang=python3
#
# [2012] Sum of Beauty in the Array
#
# https://leetcode.com/problems/sum-of-beauty-in-the-array/description/
#
# algorithms
# Medium (51.85%)
# Likes:    689
# Dislikes: 79
# Total Accepted:    34.4K
# Total Submissions: 66.4K
# Testcase Example:  "[1,2,3]"
#
# You are given a 0-indexed integer array nums. For each index i (1 <= i <=
# nums.length - 2) the beauty of nums[i] equals:
#
#
# 2, if nums[j] < nums[i] < nums[k], for all 0 <= j < i and for all i < k <=
# nums.length - 1.
#
#
# 1, if nums[i - 1] < nums[i] < nums[i + 1], and the previous condition is not
# satisfied.
#
#
# 0, if none of the previous conditions holds.
#
# Return the sum of beauty of all nums[i] where 1 <= i <= nums.length - 2.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3]
# Output: 2
# Explanation: For each index i in the range 1 <= i <= 1:
# - The beauty of nums[1] equals 2.
#
# Example 2:
#
# Input: nums = [2,4,6,4]
# Output: 1
# Explanation: For each index i in the range 1 <= i <= 2:
# - The beauty of nums[1] equals 1.
# - The beauty of nums[2] equals 0.
#
# Example 3:
#
# Input: nums = [3,2,1]
# Output: 0
# Explanation: For each index i in the range 1 <= i <= 1:
# - The beauty of nums[1] equals 0.
#
#
#
# Constraints:
#
#
# 3 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def sumOfBeauties(self, nums: List[int]) -> int:
        """
        Interview explanation:
        For each i in 1..n-2: beauty 2 if max(left)<nums[i]<min(right); else 1
        if nums[i-1]<nums[i]<nums[i+1]; else 0. Sum beauties.

        Algorithm:
        - Precompute prefix max and suffix min; scan and accumulate.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * n
        pref[0] = nums[0]
        for i in range(1, n):
            pref[i] = max(pref[i - 1], nums[i])
        suf = [0] * n
        suf[-1] = nums[-1]
        for i in range(n - 2, -1, -1):
            suf[i] = min(suf[i + 1], nums[i])
        ans = 0
        for i in range(1, n - 1):
            if pref[i - 1] < nums[i] < suf[i + 1]:
                ans += 2
            elif nums[i - 1] < nums[i] < nums[i + 1]:
                ans += 1
        return ans
# @lc code=end
