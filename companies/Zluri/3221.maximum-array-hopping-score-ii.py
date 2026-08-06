#
# @lc app=leetcode id=3221 lang=python3
#
# [3221] Maximum Array Hopping Score II
#
# https://leetcode.com/problems/maximum-array-hopping-score-ii/description/
#
# algorithms
# Medium (59.83%)
# Likes:    17
# Dislikes: 3
# Total Accepted:    1.2K
# Total Submissions: 2K
# Testcase Example:  "[1,5,8]"
#
#
# Given an array nums, you have to get the maximum score starting from
# index 0 and hopping until you reach the last element of the array.
#
# In each hop, you can jump from index i to an index j > i, and you get a
# score of (j - i) * nums[j].
#
# Return the maximum score you can get.
#
# Example 1:
#
# Input: nums = [1,5,8]
#
# Output: 16
#
# Explanation:
#
# There are two possible ways to reach the last element:
#
# 0 -> 1 -> 2 with a score of (1 - 0) * 5 + (2 - 1) * 8 = 13.
#
# 0 -> 2 with a score of (2 - 0) * 8 = 16.
#
# Example 2:
#
# Input: nums = [4,5,2,8,9,1,3]
#
# Output: 42
#
# Explanation:
#
# We can do the hopping 0 -> 4 -> 6 with a score of (4 - 0) * 9 + (6 - 4)
# * 3 = 42.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A hop i -> j scores (j - i) * nums[j]. Optimal landings are right-to-left
        maxima; each unit distance contributes the max value to its right.

        Algorithm:
        - Scan right to left keeping a running maximum mx of nums[i..n-1].
        - For each index i from n-1 down to 1, add mx to the answer
          (distance-1 segment ending at i contributes mx).

        Complexity: O(n) time, O(1) space.
        Alternate: jump only onto strict suffix maxima and evaluate the path sum.
        """
        ans = 0
        mx = 0
        for i in range(len(nums) - 1, 0, -1):
            mx = max(mx, nums[i])
            ans += mx
        return ans

# @lc code=end
