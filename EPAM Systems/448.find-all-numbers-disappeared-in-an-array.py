#
# @lc app=leetcode id=448 lang=python3
#
# [448] Find All Numbers Disappeared in an Array
#
# https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/description/
#
# algorithms
# Easy (64.5%)
# Likes:    10536
# Dislikes: 559
# Total Accepted:    1.5M
# Total Submissions: 2.3M
# Testcase Example:  "[4,3,2,7,8,2,3,1]"
#
# Given an array nums of n integers where nums[i] is in the range [1, n],
# return an array of all the integers in the range [1, n] that do not appear in
# nums.
#
# Example 1:
#
# Input: nums = [4,3,2,7,8,2,3,1]
# Output: [5,6]
#
# Example 2:
#
# Input: nums = [1,1]
# Output: [2]
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= n
#
# Follow up: Could you do it without extra space and in O(n) runtime? You may
# assume the returned list does not count as extra space.
#

# @lc code=start

from typing import List


class Solution:
    def findDisappearedNumbers(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Index-mark: for each value v, mark nums[abs(v)-1] negative. Indices
        still positive at the end correspond to missing numbers (i+1).

        Algorithm:
        - Negate nums[abs(x)-1] for each x (if not already negative).
        - Collect i+1 where nums[i] > 0.

        Complexity: O(n) time, O(1) extra space.
        """
        for x in nums:
            i = abs(x) - 1
            if nums[i] > 0:
                nums[i] = -nums[i]
        return [i + 1 for i, v in enumerate(nums) if v > 0]

    def findDisappearedNumbersSet(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: set difference between {1..n} and the numbers present.

        Algorithm:
        - Return sorted(set(range(1,n+1)) - set(nums)) or list comprehension.

        Complexity: O(n) time, O(n) space.
        """
        present = set(nums)
        return [i for i in range(1, len(nums) + 1) if i not in present]
# @lc code=end
