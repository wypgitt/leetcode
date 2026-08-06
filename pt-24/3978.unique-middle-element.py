#
# @lc app=leetcode id=3978 lang=python3
#
# [3978] Unique Middle Element
#
# https://leetcode.com/problems/unique-middle-element/description/
#
# algorithms
# Easy (72.30%)
# Likes:    26
# Dislikes: 2
# Total Accepted:    47.9K
# Total Submissions: 66.3K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums of odd length n.
#
# Return true if the middle element of nums appears exactly once in the
# array. Otherwise return false.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: true
#
# Explanation:
#
# The middle element of nums is 2, which appears exactly once.
#
# Thus, the answer is true.
#
# Example 2:
#
# Input: nums = [1,2,2]
#
# Output: false
#
# Explanation:
#
# The middle element of nums is 2, which appears twice.
#
# Thus, the answer is false.
#
# Constraints:
#
# 1 <= n == nums.length <= 100
#
# n is odd.
#
# 1 <= nums[i] <= 100
#

# @lc code=start

class Solution:
    def isMiddleElementUnique(self, nums: list[int]) -> bool:
        """
        Interview explanation:
        The middle value at index n//2 must occur exactly once in nums.

        Algorithm:
        - Read mid = nums[n//2] and return nums.count(mid) == 1.

        Complexity: O(n) time, O(1) space.
        """
        return nums.count(nums[len(nums) // 2]) == 1
# @lc code=end
