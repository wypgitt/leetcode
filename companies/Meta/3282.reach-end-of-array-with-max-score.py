#
# @lc app=leetcode id=3282 lang=python3
#
# [3282] Reach End of Array With Max Score
#
# https://leetcode.com/problems/reach-end-of-array-with-max-score/description/
#
# algorithms
# Medium (33.74%)
# Likes:    233
# Dislikes: 16
# Total Accepted:    30.1K
# Total Submissions: 89.2K
# Testcase Example:  "[1,3,1,5]"
#
#
# You are given an integer array nums of length n.
#
# Your goal is to start at index 0 and reach index n - 1. You can only
# jump to indices greater than your current index.
#
# The score for a jump from index i to index j is calculated as (j - i) *
# nums[i].
#
# Return the maximum possible total score by the time you reach the last
# index.
#
# Example 1:
#
# Input: nums = [1,3,1,5]
#
# Output: 7
#
# Explanation:
#
# First, jump to index 1 and then jump to the last index. The final score
# is 1 * 1 + 2 * 3 = 7.
#
# Example 2:
#
# Input: nums = [4,3,1,3,2]
#
# Output: 16
#
# Explanation:
#
# Jump directly to the last index. The final score is 4 * 4 = 16.
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
    def findMaximumScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A path score telescopes into a sum of unit steps, each charged to the
        jump source. Optimal: keep the strongest value seen so far as source.

        Algorithm:
        - Walk left to right; add current max for each step into the next index.
        - Raise the max whenever nums[i] is larger (new jump source).
        - Alternate: interpret as sum over i of max(nums[0..i]) for i < n-1.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        cur = nums[0]
        for i in range(1, len(nums)):
            ans += cur
            if nums[i] > cur:
                cur = nums[i]
        return ans

    def findMaximumScore_prefix_max(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Explicit prefix-max formulation of the same greedy score.

        Algorithm:
        - For each index i in [0, n-2], contribute max(nums[0..i]).

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        mx = 0
        for i in range(len(nums) - 1):
            mx = max(mx, nums[i])
            ans += mx
        return ans
# @lc code=end
