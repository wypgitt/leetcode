#
# @lc app=leetcode id=1608 lang=python3
#
# [1608] Special Array With X Elements Greater Than or Equal X
#
# https://leetcode.com/problems/special-array-with-x-elements-greater-than-or-equal-x/description/
#
# algorithms
# Easy (66.9%)
# Likes:    2358
# Dislikes: 472
# Total Accepted:    239K
# Total Submissions: 358K
# Testcase Example:  "[3,5]"
#
# You are given an array nums of non-negative integers. nums is considered
# special if there exists a number x such that there are exactly x numbers in
# nums that are greater than or equal to x.
#
# Notice that x does not have to be an element in nums.
#
# Return x if the array is special, otherwise, return -1. It can be proven that
# if nums is special, the value for x is unique.
#
# Example 1:
#
# Input: nums = [3,5]
# Output: 2
# Explanation: There are 2 values (3 and 5) that are greater than or equal to
# 2.
#
# Example 2:
#
# Input: nums = [0,0]
# Output: -1
# Explanation: No numbers fit the criteria for x.
# If x = 0, there should be 0 numbers >= x, but there are 2.
# If x = 1, there should be 1 number >= x, but there are 0.
# If x = 2, there should be 2 numbers >= x, but there are 0.
# x cannot be greater since there are only 2 numbers in nums.
#
# Example 3:
#
# Input: nums = [0,4,3,0,4]
# Output: 3
# Explanation: There are 3 values that are greater than or equal to 3.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 0 <= nums[i] <= 1000
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def specialArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Find x such that exactly x elements are >= x (or -1). Sort, then for each
        candidate x use binary search to count how many are >= x.

        Algorithm (sort + binary search count):
        - Sort nums. For x in 0..n: cnt = n - bisect_left(nums, x); if cnt==x
          return x; else -1.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        nums.sort()
        n = len(nums)
        for x in range(n + 1):
            if n - bisect.bisect_left(nums, x) == x:
                return x
        return -1

    def specialArray_counting(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate counting: freq of values capped at n; suffix counts of >=x.

        Algorithm (counting):
        - freq[min(v,n)]++; suffix from n downto 0; if suffix[x]==x return x.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        freq = [0] * (n + 1)
        for v in nums:
            freq[min(v, n)] += 1
        ge = 0
        for x in range(n, -1, -1):
            ge += freq[x]
            if ge == x:
                return x
        return -1
# @lc code=end
