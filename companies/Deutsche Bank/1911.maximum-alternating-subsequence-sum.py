#
# @lc app=leetcode id=1911 lang=python3
#
# [1911] Maximum Alternating Subsequence Sum
#
# https://leetcode.com/problems/maximum-alternating-subsequence-sum/description/
#
# algorithms
# Medium (59.24%)
# Likes:    1479
# Dislikes: 34
# Total Accepted:    71.2K
# Total Submissions: 120K
# Testcase Example:  "[4,2,5,3]"
#
# The alternating sum of a 0-indexed array is defined as the sum of the
# elements at even indices minus the sum of the elements at odd indices.
#
# For example, the alternating sum of [4,2,5,3] is (4 + 5) - (2 + 3) = 4.
#
# Given an array nums, return the maximum alternating sum of any subsequence of
# nums (after reindexing the elements of the subsequence).
#
# A subsequence of an array is a new array generated from the original array by
# deleting some elements (possibly none) without changing the remaining
# elements' relative order. For example, [2,7,4] is a subsequence of
# [4,2,3,7,2,1,4] (the underlined elements), while [2,4,2] is not.
#
# Example 1:
#
# Input: nums = [4,2,5,3]
# Output: 7
# Explanation: It is optimal to choose the subsequence [4,2,5] with alternating
# sum (4 + 5) - 2 = 7.
#
# Example 2:
#
# Input: nums = [5,6,7,8]
# Output: 8
# Explanation: It is optimal to choose the subsequence [8] with alternating sum
# 8.
#
# Example 3:
#
# Input: nums = [6,2,1,2,4,5]
# Output: 10
# Explanation: It is optimal to choose the subsequence [6,1,5] with alternating
# sum (6 + 5) - 1 = 10.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxAlternatingSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max even-index-minus-odd-index sum over any subsequence (0-index in subseq).
        DP: even = best ending with +; odd = best ending with -.

        Algorithm:
        - even=odd=0. For x: even' = max(even, odd+x); odd' = max(odd, even-x).

        Complexity: O(n) time, O(1) space.
        """
        even = odd = 0
        for x in nums:
            even, odd = max(even, odd + x), max(odd, even - x)
        return even

    def maxAlternatingSum_greedy(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Classic alternate intuition: take peaks/valleys — equivalent to summing
        positive diffs along a path; DP above is the clean optimal form.

        Algorithm:
        - Same DP renamed as take/skip polarity.

        Complexity: O(n) time, O(1) space.
        """
        return self.maxAlternatingSum(nums)
# @lc code=end
