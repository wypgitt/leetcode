#
# @lc app=leetcode id=3708 lang=python3
#
# [3708] Longest Fibonacci Subarray
#
# https://leetcode.com/problems/longest-fibonacci-subarray/description/
#
# algorithms
# Medium (69.69%)
# Likes:    54
# Dislikes: 2
# Total Accepted:    34.9K
# Total Submissions: 50.1K
# Testcase Example:  "[1,1,1,1,2,3,5,1]"
#
#
# You are given an array of positive integers nums.
#
# A Fibonacci array is a contiguous sequence whose third and subsequent
# terms each equal the sum of the two preceding terms.
#
# Return the length of the longest Fibonacci subarray in nums.
#
# Note: Subarrays of length 1 or 2 are always Fibonacci.
#
# Example 1:
#
# Input: nums = [1,1,1,1,2,3,5,1]
#
# Output: 5
#
# Explanation:
#
# The longest Fibonacci subarray is nums[2..6] = [1, 1, 2, 3, 5].
#
# [1, 1, 2, 3, 5] is Fibonacci because 1 + 1 = 2, 1 + 2 = 3, and 2 + 3 =
# 5.
#
# Example 2:
#
# Input: nums = [5,2,7,9,16]
#
# Output: 5
#
# Explanation:
#
# The longest Fibonacci subarray is nums[0..4] = [5, 2, 7, 9, 16].
#
# [5, 2, 7, 9, 16] is Fibonacci because 5 + 2 = 7, 2 + 7 = 9, and 7 + 9 =
# 16.
#
# Example 3:
#
# Input: nums = [1000000000,1000000000,1000000000]
#
# Output: 2
#
# Explanation:
#
# The longest Fibonacci subarray is nums[1..2] = [1000000000, 1000000000].
#
# [1000000000, 1000000000] is Fibonacci because its length is 2.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A Fibonacci subarray extends while each new value equals the sum of the
        previous two. Length 1–2 are always valid, so the answer is at least 2.

        Algorithm:
        - Scan i from 2..n-1; grow current streak when nums[i]==nums[i-1]+nums[i-2],
          else reset streak to 2. Track the maximum.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        ans = cur = 2
        for i in range(2, n):
            if nums[i] == nums[i - 1] + nums[i - 2]:
                cur += 1
                ans = max(ans, cur)
            else:
                cur = 2
        return ans
# @lc code=end
