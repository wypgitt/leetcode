#
# @lc app=leetcode id=1979 lang=python3
#
# [1979] Find Greatest Common Divisor of Array
#
# https://leetcode.com/problems/find-greatest-common-divisor-of-array/description/
#
# algorithms
# Easy (83.46%)
# Likes:    1480
# Dislikes: 58
# Total Accepted:    407K
# Total Submissions: 488K
# Testcase Example:  "[2,5,6,9,10]"
#
# Given an integer array nums, return the greatest common divisor of the
# smallest number and largest number in nums.
#
# The greatest common divisor of two numbers is the largest positive integer
# that evenly divides both numbers.
#
# Example 1:
#
# Input: nums = [2,5,6,9,10]
# Output: 2
# Explanation:
# The smallest number in nums is 2.
# The largest number in nums is 10.
# The greatest common divisor of 2 and 10 is 2.
#
# Example 2:
#
# Input: nums = [7,5,6,8,3]
# Output: 1
# Explanation:
# The smallest number in nums is 3.
# The largest number in nums is 8.
# The greatest common divisor of 3 and 8 is 1.
#
# Example 3:
#
# Input: nums = [3,3]
# Output: 3
# Explanation:
# The smallest number in nums is 3.
# The largest number in nums is 3.
# The greatest common divisor of 3 and 3 is 3.
#
# Constraints:
#
# 2 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List
import math


class Solution:
    def findGCD(self, nums: List[int]) -> int:
        """
        Interview explanation:
        GCD of the smallest and largest numbers in the array (any GCD of all
        would divide both min and max; problem asks gcd(min, max)).

        Algorithm:
        - return math.gcd(min(nums), max(nums)).

        Complexity: O(n + log A) time, O(1) space.
        """
        return math.gcd(min(nums), max(nums))

    def findGCD_euclidean(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: manual Euclidean algorithm on min and max.

        Algorithm:
        - a,b = min,max; while b: a,b = b, a%b; return a.

        Complexity: O(n + log A) time, O(1) space.
        """
        a, b = min(nums), max(nums)
        while b:
            a, b = b, a % b
        return a
# @lc code=end

