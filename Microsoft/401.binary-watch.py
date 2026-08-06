#
# @lc app=leetcode id=401 lang=python3
#
# [401] Binary Watch
#
# https://leetcode.com/problems/binary-watch/description/
#
# algorithms
# Easy (66.0%)
# Likes:    1987
# Dislikes: 3085
# Total Accepted:    294K
# Total Submissions: 445K
# Testcase Example:  "1"
#
# A binary watch has 4 LEDs on the top to represent the hours (0-11), and 6
# LEDs on the bottom to represent the minutes (0-59). Each LED represents a
# zero or one, with the least significant bit on the right.
#
# For example, the below binary watch reads "4:51".
#
# Given an integer turnedOn which represents the number of LEDs that are
# currently on (ignoring the PM), return all possible times the watch could
# represent. You may return the answer in any order.
#
# The hour must not contain a leading zero.
#
# For example, "01:00" is not valid. It should be "1:00".
#
# The minute must consist of two digits and may contain a leading zero.
#
# For example, "10:2" is not valid. It should be "10:02".
#
# Example 1:
#
# Input: turnedOn = 1
# Output:
# ["0:01","0:02","0:04","0:08","0:16","0:32","1:00","2:00","4:00","8:00"]
#
# Example 2:
#
# Input: turnedOn = 9
# Output: []
#
# Constraints:
#
# 0 <= turnedOn <= 10
#

# @lc code=start

from typing import List


class Solution:
    def readBinaryWatch(self, turnedOn: int) -> List[str]:
        """
        Interview explanation:
        Enumerate all valid hour/minute pairs and keep those whose LED bit
        counts sum to turnedOn. Hours use 4 bits (0-11), minutes 6 bits (0-59).

        Algorithm:
        - For h in 0..11, m in 0..59: if bit_count(h)+bit_count(m)==turnedOn,
          append f"{h}:{m:02d}".

        Complexity: O(1) time (12*60), O(1) space for output size bound.
        """
        ans = []
        for h in range(12):
            for m in range(60):
                if h.bit_count() + m.bit_count() == turnedOn:
                    ans.append(f"{h}:{m:02d}")
        return ans

    def readBinaryWatchBacktrack(self, turnedOn: int) -> List[str]:
        """
        Interview explanation:
        Alternate: backtrack over 10 LED positions (4 hour + 6 minute bits),
        choosing turnedOn bits on, then validate hour/minute ranges.

        Algorithm:
        - Recurse on LED index; when remaining==0, format if h<12 and m<60.

        Complexity: O(C(10,k)) time, O(k) recursion space.
        """
        leds = [8, 4, 2, 1, 32, 16, 8, 4, 2, 1]
        ans = []

        def dfs(i: int, left: int, h: int, m: int) -> None:
            if left == 0:
                if h < 12 and m < 60:
                    ans.append(f"{h}:{m:02d}")
                return
            if i == 10 or left > 10 - i:
                return
            # skip
            dfs(i + 1, left, h, m)
            # take
            if i < 4:
                dfs(i + 1, left - 1, h + leds[i], m)
            else:
                dfs(i + 1, left - 1, h, m + leds[i])

        dfs(0, turnedOn, 0, 0)
        return ans
# @lc code=end
