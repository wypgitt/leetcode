#
# @lc app=leetcode id=2219 lang=python3
#
# [2219] Maximum Sum Score of Array
#
# https://leetcode.com/problems/maximum-sum-score-of-array/description/
#
# algorithms
# Medium (62.90%)
# Likes:    73
# Dislikes: 19
# Total Accepted:    6K
# Total Submissions: 9.6K
# Testcase Example:  "[4,3,-2,5]"
#
#
# You are given a 0-indexed integer array nums of length n.
#
# The sum score of nums at an index i where 0 <= i < n is the maximum of:
#
# The sum of the first i + 1 elements of nums.
#
# The sum of the last n - i elements of nums.
#
# Return the maximum sum score of nums at any index.
#
# Example 1:
#
# Input: nums = [4,3,-2,5]
# Output: 10
# Explanation:
# The sum score at index 0 is max(4, 4 + 3 + -2 + 5) = max(4, 10) = 10.
# The sum score at index 1 is max(4 + 3, 3 + -2 + 5) = max(7, 6) = 7.
# The sum score at index 2 is max(4 + 3 + -2, -2 + 5) = max(5, 3) = 5.
# The sum score at index 3 is max(4 + 3 + -2 + 5, 5) = max(10, 5) = 10.
# The maximum sum score of nums is 10.
#
# Example 2:
#
# Input: nums = [-3,-5]
# Output: -3
# Explanation:
# The sum score at index 0 is max(-3, -3 + -5) = max(-3, -8) = -3.
# The sum score at index 1 is max(-3 + -5, -5) = max(-8, -5) = -5.
# The maximum sum score of nums is -3.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# @lc code=start
from typing import List


class Solution:
    def maximumSumScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Score of index i is max(prefix sum nums[0..i], suffix sum
        nums[i..n-1]). Return the maximum score over all i.

        Algorithm:
        - total = sum(nums); scan prefix; at i score = max(prefix, total-prefix+nums[i]).

        Complexity: O(n) time, O(1) space.
        """
        total = sum(nums)
        ans = float("-inf")
        pref = 0
        for x in nums:
            pref += x
            ans = max(ans, pref, total - pref + x)
        return int(ans)
# @lc code=end
