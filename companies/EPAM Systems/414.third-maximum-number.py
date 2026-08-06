#
# @lc app=leetcode id=414 lang=python3
#
# [414] Third Maximum Number
#
# https://leetcode.com/problems/third-maximum-number/description/
#
# algorithms
# Easy (40.07%)
# Likes:    3623
# Dislikes: 3599
# Total Accepted:    898K
# Total Submissions: 2.2M
# Testcase Example:  "[3,2,1]"
#
# Given an integer array nums, return the third distinct maximum number in this
# array. If the third maximum does not exist, return the maximum number.
#
# Example 1:
#
# Input: nums = [3,2,1]
# Output: 1
# Explanation:
# The first distinct maximum is 3.
# The second distinct maximum is 2.
# The third distinct maximum is 1.
#
# Example 2:
#
# Input: nums = [1,2]
# Output: 2
# Explanation:
# The first distinct maximum is 2.
# The second distinct maximum is 1.
# The third distinct maximum does not exist, so the maximum (2) is returned
# instead.
#
# Example 3:
#
# Input: nums = [2,2,3,1]
# Output: 1
# Explanation:
# The first distinct maximum is 3.
# The second distinct maximum is 2 (both 2's are counted together since they
# have the same value).
# The third distinct maximum is 1.
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -2^31 <= nums[i] <= 2^31 - 1
#
# Follow up: Can you find an O(n) solution?
#

# @lc code=start

from typing import List, Optional


class Solution:
    def thirdMax(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Track the top three distinct maxima with three variables. If fewer than
        three distinct values exist, return the maximum.

        Algorithm:
        - Scan nums; update first/second/third distinct max as needed.
        - Return third if set else first.

        Complexity: O(n) time, O(1) space.
        """
        first = second = third = None  # type: Optional[int]
        for x in nums:
            if x == first or x == second or x == third:
                continue
            if first is None or x > first:
                third, second, first = second, first, x
            elif second is None or x > second:
                third, second = second, x
            elif third is None or x > third:
                third = x
        return third if third is not None else first

    def thirdMaxSet(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: put unique values in a set; if size>=3 return 3rd largest
        else the max.

        Algorithm:
        - uniq = set(nums); return sorted(uniq)[-3] if len>=3 else max(uniq).

        Complexity: O(n log n) time, O(n) space.
        """
        uniq = set(nums)
        if len(uniq) < 3:
            return max(uniq)
        return sorted(uniq)[-3]
# @lc code=end
