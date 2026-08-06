#
# @lc app=leetcode id=41 lang=python3
#
# [41] First Missing Positive
#
# https://leetcode.com/problems/first-missing-positive/description/
#
# algorithms
# Hard (43.46%)
# Likes:    18606
# Dislikes: 1987
# Total Accepted:    1.8M
# Total Submissions: 4.2M
# Testcase Example:  "[1,2,0]"
#
# Given an unsorted integer array nums. Return the smallest positive integer
# that is not present in nums.
#
# You must implement an algorithm that runs in O(n) time and uses O(1)
# auxiliary space.
#
# Example 1:
#
# Input: nums = [1,2,0]
# Output: 3
# Explanation: The numbers in the range [1,2] are all in the array.
#
# Example 2:
#
# Input: nums = [3,4,-1,1]
# Output: 2
# Explanation: 1 is in the array but 2 is missing.
#
# Example 3:
#
# Input: nums = [7,8,9,11,12]
# Output: 1
# Explanation: The smallest positive integer 1 is missing.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -2^31 <= nums[i] <= 2^31 - 1
#

# @lc code=start
from typing import List


class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        """
        Interview explanation:
        The answer is in [1, n+1]. Place each value v in [1, n] at index v-1
        (cyclic sort / index-as-hash), then the first index i with nums[i] !=
        i+1 is the missing positive.

        Algorithm:
        - For each i, while nums[i] is in [1, n] and not already at its home
          index, swap it into place.
        - Scan for the first mismatch; if none, answer is n+1.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(nums)
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                j = nums[i] - 1
                nums[i], nums[j] = nums[j], nums[i]

        for i in range(n):
            if nums[i] != i + 1:
                return i + 1
        return n + 1
# @lc code=end
