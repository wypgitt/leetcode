#
# @lc app=leetcode id=2239 lang=python3
#
# [2239] Find Closest Number to Zero
#
# https://leetcode.com/problems/find-closest-number-to-zero/description/
#
# algorithms
# Easy (48.10%)
# Likes:    815
# Dislikes: 58
# Total Accepted:    221K
# Total Submissions: 459.6K
# Testcase Example:  "[-4,-2,1,4,8]"
#
# Given an integer array nums of size n, return the number with the value
# closest to 0 in nums. If there are multiple answers, return the number with
# the largest value.
#
#
#
# Example 1:
#
# Input: nums = [-4,-2,1,4,8]
# Output: 1
# Explanation:
# The distance from -4 to 0 is |-4| = 4.
# The distance from -2 to 0 is |-2| = 2.
# The distance from 1 to 0 is |1| = 1.
# The distance from 4 to 0 is |4| = 4.
# The distance from 8 to 0 is |8| = 8.
# Thus, the closest number to 0 in the array is 1.
#
# Example 2:
#
# Input: nums = [2,-1,1]
# Output: 1
# Explanation: 1 and -1 are both the closest numbers to 0, so 1 being larger is
# returned.
#
#
#
# Constraints:
#
#
# 1 <= n <= 1000
#
#
# -10^5 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def findClosestNumber(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Return the number closest to 0; if ties, return the larger one.

        Algorithm:
        - Track best by (abs, prefer larger value).

        Complexity: O(n) time, O(1) space.
        """
        best = nums[0]
        for x in nums:
            if abs(x) < abs(best) or (abs(x) == abs(best) and x > best):
                best = x
        return best
# @lc code=end
