#
# @lc app=leetcode id=1262 lang=python3
#
# [1262] Greatest Sum Divisible by Three
#
# https://leetcode.com/problems/greatest-sum-divisible-by-three/description/
#
# algorithms
# Medium (57.03%)
# Likes:    2425
# Dislikes: 65
# Total Accepted:    165.5K
# Total Submissions: 290.1K
# Testcase Example:  '[3,6,5,1,8]'
#
# Given an integer array nums, return the maximum possible sum of elements of
# the array such that it is divisible by three.
# 
# 
# Example 1:
# 
# 
# Input: nums = [3,6,5,1,8]
# Output: 18
# Explanation: Pick numbers 3, 6, 1 and 8 their sum is 18 (maximum sum
# divisible by 3).
# 
# Example 2:
# 
# 
# Input: nums = [4]
# Output: 0
# Explanation: Since 4 is not divisible by 3, do not pick any number.
# 
# 
# Example 3:
# 
# 
# Input: nums = [1,2,3,4,4]
# Output: 12
# Explanation: Pick numbers 1, 3, 4 and 4 their sum is 12 (maximum sum
# divisible by 3).
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 4 * 10^4
# 1 <= nums[i] <= 10^4
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxSumDivThree(self, nums: List[int]) -> int:
        dp = [0, float("-inf"), float("-inf")]

        for num in nums:
            prev = dp[:]
            for remainder, total in enumerate(prev):
                dp[(remainder + num) % 3] = max(dp[(remainder + num) % 3], total + num)

        return dp[0]
# @lc code=end

# Explanation
# -----------
# Keep dp[r] as the maximum sum seen so far with remainder r modulo 3. For each
# number, either skip it or add it to each previous remainder class. Adding num
# moves remainder r to (r + num) % 3.
#
# Only three states are needed because divisibility by 3 depends solely on the
# remainder. Copying dp before updates prevents using the same number more than
# once in a transition.
#
# Edge cases: if no positive sum with a remainder exists, it stays -inf; all
# numbers already divisible by 3 accumulate in dp[0]; answer can be 0.
#
# Time complexity: O(n).
# Space complexity: O(1), three DP states.
