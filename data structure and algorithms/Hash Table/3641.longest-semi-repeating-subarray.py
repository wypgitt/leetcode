#
# @lc app=leetcode id=3641 lang=python3
#
# [3641] Longest Semi-Repeating Subarray
#
# https://leetcode.com/problems/longest-semi-repeating-subarray/description/
#
# algorithms
# Medium (63.43%)
# Likes:    6
# Dislikes: 1
# Total Accepted:    1.1K
# Total Submissions: 1.8K
# Testcase Example:  "[1,2,3,1,2,3,4]\n2"
#
#
# You are given an integer array nums of length n and an integer k.
#
# A semi‑repeating subarray is a contiguous subarray in which at
# most k elements repeat (i.e., appear more than once).
#
# Return the length of the longest semi‑repeating subarray in nums.
#
# Example 1:
#
# Input: nums = [1,2,3,1,2,3,4], k = 2
#
# Output: 6
#
# Explanation:
#
# The longest semi-repeating subarray is [2, 3, 1, 2, 3, 4], which has two
# repeating elements (2 and 3).
#
# Example 2:
#
# Input: nums = [1,1,1,1,1], k = 4
#
# Output: 5
#
# Explanation:
#
# The longest semi-repeating subarray is [1, 1, 1, 1, 1], which has only
# one repeating element (1).
#
# Example 3:
#
# Input: nums = [1,1,1,1,1], k = 0
#
# Output: 1
#
# Explanation:
#
# The longest semi-repeating subarray is [1], which has no repeating
# elements.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 0 <= k <= nums.length
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def longestSubarray(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Longest subarray where at most k distinct values appear more than once
        ("repeating elements"). Sliding window with a frequency map and a
        counter of how many values currently have freq >= 2.

        Algorithm:
        - Expand right; when a value's freq hits 2, repeat++.
        - While repeat > k, shrink left, decrementing repeat when a value
          drops from 2 to 1.
        - Track max window length.

        Complexity: O(n) time, O(n) space.
        """
        cnt = defaultdict(int)
        ans = left = repeat = 0
        for right, x in enumerate(nums):
            cnt[x] += 1
            if cnt[x] == 2:
                repeat += 1
            while repeat > k:
                y = nums[left]
                if cnt[y] == 2:
                    repeat -= 1
                cnt[y] -= 1
                if cnt[y] == 0:
                    del cnt[y]
                left += 1
            ans = max(ans, right - left + 1)
        return ans
# @lc code=end

