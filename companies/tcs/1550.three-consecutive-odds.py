#
# @lc app=leetcode id=1550 lang=python3
#
# [1550] Three Consecutive Odds
#
# https://leetcode.com/problems/three-consecutive-odds/description/
#
# algorithms
# Easy (69.32%)
# Likes:    1422
# Dislikes: 108
# Total Accepted:    457K
# Total Submissions: 659K
# Testcase Example:  "[2,6,4,1]"
#
# Given an integer array arr, return true if there are three consecutive odd
# numbers in the array. Otherwise, return false.
#
# Example 1:
#
# Input: arr = [2,6,4,1]
# Output: false
# Explanation: There are no three consecutive odds.
#
# Example 2:
#
# Input: arr = [1,2,34,3,4,5,7,23,12]
# Output: true
# Explanation: [5,7,23] are three consecutive odds.
#
# Constraints:
#
# 1 <= arr.length <= 1000
#
# 1 <= arr[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def threeConsecutiveOdds(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Return whether any three consecutive elements are all odd.

        Algorithm:
        - Scan i=0..n-3; check arr[i],arr[i+1],arr[i+2] all odd (x%2==1).

        Complexity: O(n) time, O(1) space.
        """
        streak = 0
        for x in arr:
            if x % 2 == 1:
                streak += 1
                if streak == 3:
                    return True
            else:
                streak = 0
        return False

    def threeConsecutiveOdds_window(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: explicit check of every window of three consecutive elements.

        Algorithm:
        - for i in 0..n-3: if all three odd return True.

        Complexity: O(n) time, O(1) space.
        """
        for i in range(len(arr) - 2):
            if arr[i] % 2 and arr[i + 1] % 2 and arr[i + 2] % 2:
                return True
        return False
# @lc code=end
