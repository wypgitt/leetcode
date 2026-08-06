#
# @lc app=leetcode id=4011 lang=python3
#
# [4011] Count Subarrays With Even Odd Ratio I
#
# https://leetcode.com/problems/count-subarrays-with-even-odd-ratio-i/description/
#
# algorithms
# Medium (60.57%)
# Likes:    33
# Dislikes: 3
# Total Accepted:    35.7K
# Total Submissions: 58.9K
# Testcase Example:  "[1,2,1,2]\n3\n2"
#
#
# You are given an integer array nums and two integers a and b.
#
# For a subarray, let:
#
# x be the number of even elements.
#
# y be the number of odd elements.
#
# The ratio of even to odd elements in a subarray is defined as x / y,
# where ratios are compared by their exact rational values.
#
# A subarray is considered valid if:
#
# y > 0, and
#
# x / y <= a / b.
#
# Return the number of valid subarrays in nums.
#
# Example 1:
#
# Input: nums = [1,2,1,2], a = 3, b = 2
#
# Output: 7
#
# Explanation:
#
# The following are the valid subarrays:
#
#                         Subarray
#                         Values
#                         Even Count
#                         Odd Count
#                         Ratio
#
#                         nums[0..0]
#                         [1]
#                         0
#                         1
#                         0 / 1
#
#                         nums[0..1]
#                         [1, 2]
#                         1
#                         1
#                         1 / 1
#
#                         nums[0..2]
#                         [1, 2, 1]
#                         1
#                         2
#                         1 / 2
#
#                         nums[0..3]
#                         [1, 2, 1, 2]
#                         2
#                         2
#                         2 / 2
#
#                         nums[1..2]
#                         [2, 1]
#                         1
#                         1
#                         1 / 1
#
#                         nums[2..2]
#                         [1]
#                         0
#                         1
#                         0 / 1
#
#                         nums[2..3]
#                         [1, 2]
#                         1
#                         1
#                         1 / 1
#
# Thus, the number of valid subarrays is 7.
#
# Example 2:
#
# Input: nums = [2,2,1], a = 2, b = 1
#
# Output: 3
#
# Explanation:
#
# The following are the valid subarrays:
#
#                         Subarray
#                         Values
#                         Even Count
#                         Odd Count
#                         Ratio
#
#                         nums[0..2]
#                         [2, 2, 1]
#                         2
#                         1
#                         2 / 1
#
#                         nums[1..2]
#                         [2, 1]
#                         1
#                         1
#                         1 / 1
#
#                         nums[2..2]
#                         [1]
#                         0
#                         1
#                         0 / 1
#
# Thus, the number of valid subarrays is 3.
#
# Example 3:
#
# Input: nums = [2,2,2], a = 1, b = 1
#
# Output: 0
#
# Explanation:
#
# Every subarray contains 0 odd numbers, so no subarray is valid.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#
# 1 <= a, b <= 1000
#

# @lc code=start
class Solution:
    def countRatioSubarrays(self, nums: list[int], a: int, b: int) -> int:
        """
        Interview explanation:
        Count subarrays with ≥1 odd and even/odd ratio ≤ a/b
        (equivalently b·even ≤ a·odd).

        Algorithm:
        - O(n^2) enumerate all subarrays; maintain odd count while extending.

        Complexity: O(n^2) time, O(1) space (n ≤ 1000).
        """
        ans = 0
        n = len(nums)
        for i in range(n):
            odd = 0
            for j in range(i, n):
                odd += nums[j] & 1
                even = j - i + 1 - odd
                if odd and even * b <= odd * a:
                    ans += 1
        return ans
# @lc code=end
