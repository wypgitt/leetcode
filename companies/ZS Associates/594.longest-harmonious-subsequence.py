#
# @lc app=leetcode id=594 lang=python3
#
# [594] Longest Harmonious Subsequence
#
# https://leetcode.com/problems/longest-harmonious-subsequence/description/
#
# algorithms
# Easy (64.95%)
# Likes:    2868
# Dislikes: 356
# Total Accepted:    404K
# Total Submissions: 622K
# Testcase Example:  "[1,3,2,2,5,2,3,7]"
#
# We define a harmonious array as an array where the difference between its
# maximum value and its minimum value is exactly 1.
#
# Given an integer array nums, return the length of its longest harmonious
# subsequence among all its possible subsequences.
#
# Example 1:
#
# Input: nums = [1,3,2,2,5,2,3,7]
#
# Output: 5
#
# Explanation:
#
# The longest harmonious subsequence is [3,2,2,2,3].
#
# Example 2:
#
# Input: nums = [1,2,3,4]
#
# Output: 2
#
# Explanation:
#
# The longest harmonious subsequences are [1,2], [2,3], and [3,4], all of which
# have a length of 2.
#
# Example 3:
#
# Input: nums = [1,1,1,1]
#
# Output: 0
#
# Explanation:
#
# No harmonic subsequence exists.
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# -10^9 <= nums[i] <= 10^9
#


# @lc code=start
from collections import Counter
from typing import List
class Solution:
    def findLHS(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A harmonious subsequence's max - min = 1, so it uses exactly two
        consecutive integer values. Count frequencies; for each value x, if
        x+1 exists, candidate length is count[x] + count[x+1].

        Algorithm:
        - freq = Counter(nums).
        - For each x in freq, if x+1 in freq, update ans with freq[x]+freq[x+1].

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter(nums)
        ans = 0
        for x, c in freq.items():
            if x + 1 in freq:
                ans = max(ans, c + freq[x + 1])
        return ans

    def findLHSSortWindow(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sort then use a sliding window: expand right; when nums[right]-nums[left]
        > 1 shrink left; when difference is exactly 1, window length is a candidate.

        Algorithm:
        - Sort nums; two pointers left/right maintain max-min <= 1.
        - When == 1, update answer with right-left+1.

        Complexity: O(n log n) time, O(n) space for sort.
        """
        nums = sorted(nums)
        ans = 0
        left = 0
        for right in range(len(nums)):
            while nums[right] - nums[left] > 1:
                left += 1
            if nums[right] - nums[left] == 1:
                ans = max(ans, right - left + 1)
        return ans
# @lc code=end

