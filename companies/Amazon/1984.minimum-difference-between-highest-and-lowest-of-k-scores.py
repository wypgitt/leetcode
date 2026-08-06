#
# @lc app=leetcode id=1984 lang=python3
#
# [1984] Minimum Difference Between Highest and Lowest of K Scores
#
# https://leetcode.com/problems/minimum-difference-between-highest-and-lowest-of-k-scores/description/
#
# algorithms
# Easy (66.35%)
# Likes:    1476
# Dislikes: 380
# Total Accepted:    265K
# Total Submissions: 399K
# Testcase Example:  "[90]"
#
# You are given a 0-indexed integer array nums, where nums[i] represents the
# score of the i^th student. You are also given an integer k.
#
# Pick the scores of any k students from the array so that the difference
# between the highest and the lowest of the k scores is minimized.
#
# Return the minimum possible difference.
#
# Example 1:
#
# Input: nums = [90], k = 1
# Output: 0
# Explanation: There is one way to pick score(s) of one student:
# - [90]. The difference between the highest and lowest score is 90 - 90 = 0.
# The minimum possible difference is 0.
#
# Example 2:
#
# Input: nums = [9,4,1,7], k = 2
# Output: 2
# Explanation: There are six ways to pick score(s) of two students:
# - [9,4,1,7]. The difference between the highest and lowest score is 9 - 4 =
# 5.
# - [9,4,1,7]. The difference between the highest and lowest score is 9 - 1 =
# 8.
# - [9,4,1,7]. The difference between the highest and lowest score is 9 - 7 =
# 2.
# - [9,4,1,7]. The difference between the highest and lowest score is 4 - 1 =
# 3.
# - [9,4,1,7]. The difference between the highest and lowest score is 7 - 4 =
# 3.
# - [9,4,1,7]. The difference between the highest and lowest score is 7 - 1 =
# 6.
# The minimum possible difference is 2.
#
# Constraints:
#
# 1 <= k <= nums.length <= 1000
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minimumDifference(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Choose any k scores; minimize max-min among them. Sort and slide a
        window of size k.

        Algorithm:
        - Sort; ans = min(nums[i+k-1]-nums[i]) over i.

        Complexity: O(n log n) time, O(n) space if sort copies else O(1) extra.
        """
        nums = sorted(nums)
        return min(nums[i + k - 1] - nums[i] for i in range(len(nums) - k + 1))

    def minimumDifference_loop(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate explicit loop for the sliding-window minimum after sorting.

        Algorithm:
        - Sort; track running min of window maxima-minima.

        Complexity: O(n log n) time, O(1) extra besides sort.
        """
        nums.sort()
        ans = 10**18
        for i in range(len(nums) - k + 1):
            ans = min(ans, nums[i + k - 1] - nums[i])
        return int(ans)
# @lc code=end

