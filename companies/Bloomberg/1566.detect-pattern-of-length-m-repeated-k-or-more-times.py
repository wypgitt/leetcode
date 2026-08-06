#
# @lc app=leetcode id=1566 lang=python3
#
# [1566] Detect Pattern of Length M Repeated K or More Times
#
# https://leetcode.com/problems/detect-pattern-of-length-m-repeated-k-or-more-times/description/
#
# algorithms
# Easy (44.12%)
# Likes:    699
# Dislikes: 149
# Total Accepted:    48.1K
# Total Submissions: 109K
# Testcase Example:  "[1,2,4,4,4,4]"
#
# Given an array of positive integers arr, find a pattern of length m that is
# repeated k or more times.
#
# A pattern is a subarray (consecutive sub-sequence) that consists of one or
# more values, repeated multiple times consecutively without overlapping. A
# pattern is defined by its length and the number of repetitions.
#
# Return true if there exists a pattern of length m that is repeated k or more
# times, otherwise return false.
#
# Example 1:
#
# Input: arr = [1,2,4,4,4,4], m = 1, k = 3
# Output: true
# Explanation: The pattern (4) of length 1 is repeated 4 consecutive times.
# Notice that pattern can be repeated k or more times but not less.
#
# Example 2:
#
# Input: arr = [1,2,1,2,1,1,1,3], m = 2, k = 2
# Output: true
# Explanation: The pattern (1,2) of length 2 is repeated 2 consecutive times.
# Another valid pattern (2,1) is also repeated 2 times.
#
# Example 3:
#
# Input: arr = [1,2,1,2,1,3], m = 2, k = 3
# Output: false
# Explanation: The pattern (1,2) is of length 2 but is repeated only 2 times.
# There is no pattern of length 2 that is repeated 3 or more times.
#
# Constraints:
#
# 2 <= arr.length <= 100
#
# 1 <= arr[i] <= 100
#
# 1 <= m <= 100
#
# 2 <= k <= 100
#

# @lc code=start
from typing import List


class Solution:
    def containsPattern(self, arr: List[int], m: int, k: int) -> bool:
        """
        Interview explanation:
        Look for m-length pattern repeated k consecutive times. Scan starts;
        compare arr[i:i+m] with next k-1 blocks, or count consecutive matching
        m-steps.

        Algorithm (run length of equal m-gaps):
        - need (k-1)*m consecutive positions where arr[i]==arr[i+m].
        - Walk i; streak of matches; if streak >= (k-1)*m return True.

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        need = (k - 1) * m
        if need == 0:
            return True
        streak = 0
        for i in range(n - m):
            if arr[i] == arr[i + m]:
                streak += 1
                if streak >= need:
                    return True
            else:
                streak = 0
        return False

    def containsPattern_slice(self, arr: List[int], m: int, k: int) -> bool:
        """
        Interview explanation:
        Alternate: for each start, check arr[start:start+m] * k equals the
        following slice of length m*k.

        Algorithm:
        - for i in range(n-m*k+1): if arr[i:i+m]*k == arr[i:i+m*k]: True

        Complexity: O(n*m*k) time.
        """
        n = len(arr)
        total = m * k
        for i in range(n - total + 1):
            if arr[i : i + m] * k == arr[i : i + total]:
                return True
        return False
# @lc code=end

