#
# @lc app=leetcode id=3925 lang=python3
#
# [3925] Concatenate Array With Reverse
#
# https://leetcode.com/problems/concatenate-array-with-reverse/description/
#
# algorithms
# Easy (91.68%)
# Likes:    39
# Dislikes: 2
# Total Accepted:    66.7K
# Total Submissions: 72.7K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums of length n.
#
# Construct a new array ans of length 2 * n such that the first n elements
# are the same as nums, and the next n elements are the elements of nums
# in reverse order.
#
# Formally, for 0 <= i <= n - 1:
#
# ans[i] = nums[i]
#
# ans[i + n] = nums[n - i - 1]
#
# Return an integer array ans.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: [1,2,3,3,2,1]
#
# Explanation:
#
# The first n elements of ans are the same as nums.
#
# For the next n = 3 elements, each element is taken from nums in reverse
# order:
#
# ans[3] = nums[2] = 3
#
# ans[4] = nums[1] = 2
#
# ans[5] = nums[0] = 1
#
# Thus, ans = [1, 2, 3, 3, 2, 1].
#
# Example 2:
#
# Input: nums = [1]
#
# Output: [1,1]
#
# Explanation:
#
# The array remains the same when reversed. Thus, ans = [1, 1].
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start

class Solution:
    def concatWithReverse(self, nums: list[int]) -> list[int]:
        """
        Interview explanation:
        Build ans = nums followed by nums reversed.

        Algorithm:
        - Return nums + nums[::-1].

        Complexity: O(n) time, O(n) space.
        """
        return nums + nums[::-1]

    def concatWithReverse_manual(self, nums: list[int]) -> list[int]:
        """
        Interview explanation:
        Alternate: allocate 2n and fill both halves by index.

        Algorithm:
        - ans[i] = nums[i], ans[i+n] = nums[n-1-i].

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        ans = [0] * (2 * n)
        for i in range(n):
            ans[i] = nums[i]
            ans[i + n] = nums[n - 1 - i]
        return ans
# @lc code=end
