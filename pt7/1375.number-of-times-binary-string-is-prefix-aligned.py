#
# @lc app=leetcode id=1375 lang=python3
#
# [1375] Number of Times Binary String Is Prefix-Aligned
#
# https://leetcode.com/problems/number-of-times-binary-string-is-prefix-aligned/description/
#
# algorithms
# Medium (66.05%)
# Likes:    969
# Dislikes: 139
# Total Accepted:    60.5K
# Total Submissions: 91.6K
# Testcase Example:  '[3,2,4,1,5]'
#
# You have a 1-indexed binary string of length n where all the bits are 0
# initially. We will flip all the bits of this binary string (i.e., change them
# from 0 to 1) one by one. You are given a 1-indexed integer array flips where
# flips[i] indicates that the bit at index flips[i] will be flipped in the i^th
# step.
# 
# A binary string is prefix-aligned if, after the i^th step, all the bits in
# the inclusive range [1, i] are ones and all the other bits are zeros.
# 
# Return the number of times the binary string is prefix-aligned during the
# flipping process.
# 
# 
# Example 1:
# 
# 
# Input: flips = [3,2,4,1,5]
# Output: 2
# Explanation: The binary string is initially "00000".
# After applying step 1: The string becomes "00100", which is not
# prefix-aligned.
# After applying step 2: The string becomes "01100", which is not
# prefix-aligned.
# After applying step 3: The string becomes "01110", which is not
# prefix-aligned.
# After applying step 4: The string becomes "11110", which is prefix-aligned.
# After applying step 5: The string becomes "11111", which is prefix-aligned.
# We can see that the string was prefix-aligned 2 times, so we return 2.
# 
# 
# Example 2:
# 
# 
# Input: flips = [4,1,2,3]
# Output: 1
# Explanation: The binary string is initially "0000".
# After applying step 1: The string becomes "0001", which is not
# prefix-aligned.
# After applying step 2: The string becomes "1001", which is not
# prefix-aligned.
# After applying step 3: The string becomes "1101", which is not
# prefix-aligned.
# After applying step 4: The string becomes "1111", which is prefix-aligned.
# We can see that the string was prefix-aligned 1 time, so we return 1.
# 
# 
# 
# Constraints:
# 
# 
# n == flips.length
# 1 <= n <= 5 * 10^4
# flips is a permutation of the integers in the range [1, n].
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def numTimesAllBlue(self, flips: List[int]) -> int:
        max_position = 0
        moments = 0

        for step, position in enumerate(flips, start=1):
            max_position = max(max_position, position)
            if max_position == step:
                moments += 1

        return moments
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# After `step` flips, exactly `step` bits are on. The prefix is all blue if and
# only if the largest flipped position is also `step`; then the flipped set must
# be exactly positions 1 through `step`.
#
# Data structure:
# Only one integer, `max_position`, is needed.
#
# Walkthrough:
# 1. Process flips in order with 1-based step count.
# 2. Update the farthest position that has been flipped.
# 3. If `max_position == step`, all positions before it must have been flipped
#    already, so count this moment.
#
# Edge cases:
# - First flip is position 1: counts immediately.
# - Large position flipped early: no count until enough earlier positions are
#   flipped.
# - Final step always counts because all positions are flipped.
#
# Complexity:
# - Time: O(n).
# - Space: O(1).
