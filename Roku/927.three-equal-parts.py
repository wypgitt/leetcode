#
# @lc app=leetcode id=927 lang=python3
#
# [927] Three Equal Parts
#
# https://leetcode.com/problems/three-equal-parts/description/
#
# algorithms
# Hard (41.55%)
# Likes:    859
# Dislikes: 127
# Total Accepted:    35.9K
# Total Submissions: 86.5K
# Testcase Example:  "[1,0,1,0,1]"
#
# You are given an array arr which consists of only zeros and ones, divide the
# array into three non-empty parts such that all of these parts represent the
# same binary value.
#
# If it is possible, return any [i, j] with i + 1 < j, such that:
#
# arr[0], arr[1], ..., arr[i] is the first part,
#
# arr[i + 1], arr[i + 2], ..., arr[j - 1] is the second part, and
#
# arr[j], arr[j + 1], ..., arr[arr.length - 1] is the third part.
#
# All three parts have equal binary values.
#
# If it is not possible, return [-1, -1].
#
# Note that the entire part is used when considering what binary value it
# represents. For example, [1,1,0] represents 6 in decimal, not 3. Also,
# leading zeros are allowed, so [0,1,1] and [1,1] represent the same value.
#
# Example 1:
#
# Input: arr = [1,0,1,0,1]
# Output: [0,3]
#
# Example 2:
#
# Input: arr = [1,1,0,1,1]
# Output: [-1,-1]
#
# Example 3:
#
# Input: arr = [1,1,0,0,1]
# Output: [0,2]
#
# Constraints:
#
# 3 <= arr.length <= 3 * 10^4
#
# arr[i] is 0 or 1
#

# @lc code=start
from typing import List


class Solution:
    def threeEqualParts(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        Three parts equal as binary numbers iff they have the same bit pattern
        (leading zeros allowed only as padding on the left of each part). Count
        ones; total ones must be divisible by 3. Find the ends of the three
        equal-one segments from the right pattern of ones, then verify equality.

        Algorithm:
        - ones = sum(arr); if ones==0: return [0, n-1] (any valid split)
        - if ones % 3: return [-1,-1]
        - target = ones // 3; find indices of 1st, (target+1)th, (2*target+1)th one
          as starts of the three patterns
        - Walk three pointers in lockstep until end; if mismatch → [-1,-1]
        - Return [i-1, j] for ends of first two parts

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        total = sum(arr)
        if total % 3:
            return [-1, -1]
        if total == 0:
            return [0, n - 1]
        k = total // 3
        first = second = third = -1
        cnt = 0
        for i, v in enumerate(arr):
            if v:
                cnt += 1
                if cnt == 1:
                    first = i
                elif cnt == k + 1:
                    second = i
                elif cnt == 2 * k + 1:
                    third = i
                    break
        # Compare patterns starting at first, second, third
        while third < n:
            if arr[first] != arr[second] or arr[second] != arr[third]:
                return [-1, -1]
            first += 1
            second += 1
            third += 1
        return [first - 1, second]
# @lc code=end

