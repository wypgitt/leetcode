#
# @lc app=leetcode id=3201 lang=python3
#
# [3201] Find the Maximum Length of Valid Subsequence I
#
# https://leetcode.com/problems/find-the-maximum-length-of-valid-subsequence-i/description/
#
# algorithms
# Medium (54.90%)
# Likes:    644
# Dislikes: 56
# Total Accepted:    143.4K
# Total Submissions: 261.2K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given an integer array nums.
#
# A subsequence sub of nums with length x is called valid if it satisfies:
#
# (sub[0] + sub[1]) % 2 == (sub[1] + sub[2]) % 2 == ... == (sub[x - 2] +
# sub[x - 1]) % 2.
#
# Return the length of the longest valid subsequence of nums.
#
# A subsequence is an array that can be derived from another array by
# deleting some or no elements without changing the order of the remaining
# elements.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
#
# Output: 4
#
# Explanation:
#
# The longest valid subsequence is [1, 2, 3, 4].
#
# Example 2:
#
# Input: nums = [1,2,1,1,2,1,2]
#
# Output: 6
#
# Explanation:
#
# The longest valid subsequence is [1, 2, 1, 2, 1, 2].
#
# Example 3:
#
# Input: nums = [1,3]
#
# Output: 2
#
# Explanation:
#
# The longest valid subsequence is [1, 3].
#
# Constraints:
#
# 2 <= nums.length <= 2 * 10^5
#
# 1 <= nums[i] <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def maximumLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A subsequence is valid iff every adjacent pair has the same sum parity.
        That means either all elements share one parity, or parities strictly
        alternate.

        Algorithm:
        - Same parity: answer is max(count even, count odd).
        - Alternating: one-pass DP — even_end / odd_end store longest alternating
          subsequence ending with that parity; update as nums is scanned.
        - Return the max of both families.

        Complexity: O(n) time, O(1) space.
        """
        even = odd = 0
        even_end = odd_end = 0
        for x in nums:
            if x & 1:
                odd += 1
                odd_end = even_end + 1
            else:
                even += 1
                even_end = odd_end + 1
        return max(even, odd, even_end, odd_end)
# @lc code=end
