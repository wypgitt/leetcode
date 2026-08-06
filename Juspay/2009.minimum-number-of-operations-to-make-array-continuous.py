#
# @lc app=leetcode id=2009 lang=python3
#
# [2009] Minimum Number of Operations to Make Array Continuous
#
# https://leetcode.com/problems/minimum-number-of-operations-to-make-array-continuous/description/
#
# algorithms
# Hard (51.77%)
# Likes:    2012
# Dislikes: 56
# Total Accepted:    89.7K
# Total Submissions: 173.2K
# Testcase Example:  "[4,2,5,3]"
#
# You are given an integer array nums. In one operation, you can replace any
# element in nums with any integer.
#
# nums is considered continuous if both of the following conditions are
# fulfilled:
#
#
# All elements in nums are unique.
#
#
# The difference between the maximum element and the minimum element in nums
# equals nums.length - 1.
#
# For example, nums = [4, 2, 5, 3] is continuous, but nums = [1, 2, 3, 5, 6] is
# not continuous.
#
# Return the minimum number of operations to make nums continuous.
#
#
#
# Example 1:
#
# Input: nums = [4,2,5,3]
# Output: 0
# Explanation: nums is already continuous.
#
# Example 2:
#
# Input: nums = [1,2,3,5,6]
# Output: 1
# Explanation: One possible solution is to change the last element to 4.
# The resulting array is [1,2,3,5,4], which is continuous.
#
# Example 3:
#
# Input: nums = [1,10,100,1000]
# Output: 3
# Explanation: One possible solution is to:
# - Change the second element to 2.
# - Change the third element to 3.
# - Change the fourth element to 4.
# The resulting array is [1,2,3,4], which is continuous.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Make nums continuous: sorted unique values form [x, x+n-1]. Each replace
        counts as one op. Minimize ops = n - max unique values spannable in a
        window of length n.

        Algorithm:
        - Sort unique; for each left, binary-search rightmost <= uniq[left]+n-1;
          maximize window size; answer n - that max.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        uniq = sorted(set(nums))
        ans = n
        for i, x in enumerate(uniq):
            j = bisect.bisect_right(uniq, x + n - 1)
            ans = min(ans, n - (j - i))
        return ans

    def minOperations_two_pointers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same idea with two pointers on sorted unique array.

        Algorithm:
        - Expand right while uniq[right]-uniq[left] <= n-1; track max window.

        Complexity: O(n log n) time (sort), O(n) space.
        """
        n = len(nums)
        uniq = sorted(set(nums))
        m = len(uniq)
        best = 0
        r = 0
        for l in range(m):
            while r < m and uniq[r] - uniq[l] <= n - 1:
                r += 1
            best = max(best, r - l)
        return n - best
# @lc code=end
