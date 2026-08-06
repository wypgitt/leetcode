#
# @lc app=leetcode id=3158 lang=python3
#
# [3158] Find the XOR of Numbers Which Appear Twice
#
# https://leetcode.com/problems/find-the-xor-of-numbers-which-appear-twice/description/
#
# algorithms
# Easy (79.22%)
# Likes:    178
# Dislikes: 15
# Total Accepted:    84.1K
# Total Submissions: 106.2K
# Testcase Example:  "[1,2,1,3]"
#
#
# You are given an array nums, where each number in the array appears
# either once or twice.
#
# Return the bitwise XOR of all the numbers that appear twice in the
# array, or 0 if no number appears twice.
#
# Example 1:
#
# Input: nums = [1,2,1,3]
#
# Output: 1
#
# Explanation:
#
# The only number that appears twice in nums is 1.
#
# Example 2:
#
# Input: nums = [1,2,3]
#
# Output: 0
#
# Explanation:
#
# No number appears twice in nums.
#
# Example 3:
#
# Input: nums = [1,2,2,1]
#
# Output: 3
#
# Explanation:
#
# Numbers 1 and 2 appeared twice. 1 XOR 2 == 3.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 50
#
# Each number in nums appears either once or twice.
#

# @lc code=start
from typing import List


class Solution:
    def duplicateNumbersXOR(self, nums: List[int]) -> int:
        """
        Interview explanation:
        XOR together every value that appears twice (or 0 if none).

        Algorithm:
        - Count frequencies; XOR keys with count == 2.

        Complexity: O(n) time, O(n) space.
        """
        from collections import Counter

        ans = 0
        for v, c in Counter(nums).items():
            if c == 2:
                ans ^= v
        return ans

    def duplicateNumbersXOR_bit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: values are in 1..50 — track seen with a bitmask / set toggle.

        Algorithm:
        - First sighting: add to set; second sighting: XOR into answer.

        Complexity: O(n) time, O(U) space.
        """
        seen = set()
        ans = 0
        for v in nums:
            if v in seen:
                ans ^= v
            else:
                seen.add(v)
        return ans
# @lc code=end
