#
# @lc app=leetcode id=3866 lang=python3
#
# [3866] First Unique Even Element
#
# https://leetcode.com/problems/first-unique-even-element/description/
#
# algorithms
# Easy (66.25%)
# Likes:    49
# Dislikes: 0
# Total Accepted:    52.6K
# Total Submissions: 79.4K
# Testcase Example:  "[3,4,2,5,4,6]"
#
#
# You are given an integer array nums.
#
# Return an integer denoting the first even integer (earliest by array
# index) that appears exactly once in nums. If no such integer exists,
# return -1.
#
# An integer x is considered even if it is divisible by 2.
#
# Example 1:
#
# Input: nums = [3,4,2,5,4,6]
#
# Output: 2
#
# Explanation:
#
# Both 2 and 6 are even and they appear exactly once. Since 2 occurs first
# in the array, the answer is 2.
#
# Example 2:
#
# Input: nums = [4,4]
#
# Output: -1
#
# Explanation:
#
# No even integer appears exactly once, so return -1.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from collections import Counter


class Solution:
    def firstUniqueEven(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Find the earliest even value that occurs exactly once.

        Algorithm:
        - Count frequencies.
        - Scan left→right; return first even with count 1, else -1.

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter(nums)
        for x in nums:
            if x % 2 == 0 and freq[x] == 1:
                return x
        return -1
# @lc code=end
