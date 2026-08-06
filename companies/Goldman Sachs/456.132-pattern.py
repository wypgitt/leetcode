#
# @lc app=leetcode id=456 lang=python3
#
# [456] 132 Pattern
#
# https://leetcode.com/problems/132-pattern/description/
#
# algorithms
# Medium (35.0%)
# Likes:    7687
# Dislikes: 474
# Total Accepted:    338K
# Total Submissions: 965K
# Testcase Example:  "[1,2,3,4]"
#
# Given an array of n integers nums, a 132 pattern is a subsequence of three
# integers nums[i], nums[j] and nums[k] such that i < j < k and nums[i] <
# nums[k] < nums[j].
#
# Return true if there is a 132 pattern in nums, otherwise, return false.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: false
# Explanation: There is no 132 pattern in the sequence.
#
# Example 2:
#
# Input: nums = [3,1,4,2]
# Output: true
# Explanation: There is a 132 pattern in the sequence: [1, 4, 2].
#
# Example 3:
#
# Input: nums = [-1,3,2,0]
# Output: true
# Explanation: There are three 132 patterns in the sequence: [-1, 3, 2], [-1,
# 3, 0] and [-1, 2, 0].
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 2 * 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def find132pattern(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Find i < j < k with nums[i] < nums[k] < nums[j]. Scan right-to-left:
        maintain a decreasing stack of candidates for nums[j], and track the
        best "ak" (nums[k]) popped below the stack top. When nums[i] < ak,
        we have a 132 pattern.

        Algorithm:
        - stack = []; ak = -inf.
        - For i from n-1..0:
          if nums[i] < ak: return True
          while stack and stack[-1] < nums[i]: ak = stack.pop()
          stack.append(nums[i])
        - Return False.

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        ak = float("-inf")
        for num in reversed(nums):
            if num < ak:
                return True
            while stack and stack[-1] < num:
                ak = stack.pop()
            stack.append(num)
        return False
# @lc code=end
