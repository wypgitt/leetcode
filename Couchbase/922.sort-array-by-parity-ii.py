#
# @lc app=leetcode id=922 lang=python3
#
# [922] Sort Array By Parity II
#
# https://leetcode.com/problems/sort-array-by-parity-ii/description/
#
# algorithms
# Easy (71.34%)
# Likes:    2851
# Dislikes: 105
# Total Accepted:    364K
# Total Submissions: 511K
# Testcase Example:  "[4,2,5,7]"
#
# Given an array of integers nums, half of the integers in nums are odd, and
# the other half are even.
#
# Sort the array so that whenever nums[i] is odd, i is odd, and whenever
# nums[i] is even, i is even.
#
# Return any answer array that satisfies this condition.
#
# Example 1:
#
# Input: nums = [4,2,5,7]
# Output: [4,5,2,7]
# Explanation: [4,7,2,5], [2,5,4,7], [2,7,4,5] would also have been accepted.
#
# Example 2:
#
# Input: nums = [2,3]
# Output: [2,3]
#
# Constraints:
#
# 2 <= nums.length <= 2 * 10^4
#
# nums.length is even.
#
# Half of the integers in nums are even.
#
# 0 <= nums[i] <= 1000
#
# Follow Up: Could you solve it in-place?
#

# @lc code=start
from typing import List


class Solution:
    def sortArrayByParityII(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        In-place two pointers: even indices must hold even values. Walk even
        slots; when odd is found, find an odd-index holding an even and swap.

        Algorithm (two pointers in-place):
        - i=0 (even), j=1 (odd)
        - While i < n: if nums[i] odd, advance j until nums[j] even, swap; i+=2

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(nums)
        j = 1
        for i in range(0, n, 2):
            if nums[i] % 2:
                while nums[j] % 2:
                    j += 2
                nums[i], nums[j] = nums[j], nums[i]
        return nums

    def sortArrayByParityII_two_arrays(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: collect evens and odds, then interleave into a result array.

        Algorithm:
        - evens = [x for x in nums if x%2==0]; odds similarly
        - Place even at even indices, odd at odd indices

        Complexity: O(n) time, O(n) space.
        """
        evens = [x for x in nums if x % 2 == 0]
        odds = [x for x in nums if x % 2 == 1]
        res = [0] * len(nums)
        for i, e in enumerate(evens):
            res[2 * i] = e
        for i, o in enumerate(odds):
            res[2 * i + 1] = o
        return res
# @lc code=end

