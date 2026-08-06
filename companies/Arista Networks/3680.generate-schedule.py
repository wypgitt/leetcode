#
# @lc app=leetcode id=3680 lang=python3
#
# [3680] Generate Schedule
#
# https://leetcode.com/problems/generate-schedule/description/
#
# algorithms
# Medium (24.99%)
# Likes:    52
# Dislikes: 25
# Total Accepted:    5K
# Total Submissions: 20K
# Testcase Example:  "3"
#
#
# You are given an integer n representing n teams. You are asked to
# generate a schedule such that:
#
# Each team plays every other team exactly twice: once at home and once
# away.
#
# There is exactly one match per day; the schedule is a list of
# consecutive days and schedule[i] is the match on day i.
#
# No team plays on consecutive days.
#
# Return a 2D integer array schedule, where schedule[i][0] represents the
# home team and schedule[i][1] represents the away team. If multiple
# schedules meet the conditions, return any one of them.
#
# If no schedule exists that meets the conditions, return an empty array.
#
# Example 1:
#
# Input: n = 3
#
# Output: []
#
# Explanation:
#
# ​​​​​​​Since each team plays every other team exactly twice, a total of
# 6 matches need to be played: [0,1],[0,2],[1,2],[1,0],[2,0],[2,1].
#
# It's not possible to create a schedule without at least one team playing
# consecutive days.
#
# Example 2:
#
# Input: n = 5
#
# Output:
# [[0,1],[2,3],[0,4],[1,2],[3,4],[0,2],[1,3],[2,4],[0,3],[1,4],[2,0],[3,1],[4,0],[2,1],[4,3],[1,0],[3,2],[4,1],[3,0],[4,2]]
#
# Explanation:
#
# Since each team plays every other team exactly twice, a total of 20
# matches need to be played.
#
# The output shows one of the schedules that meet the conditions. No team
# plays on consecutive days.
#
# Constraints:
#
# 2 <= n <= 50​​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def generateSchedule(self, n: int) -> List[List[int]]:
        """
        Interview explanation:
        Need a double round-robin (each ordered pair once) with no team on two
        consecutive days. For n <= 4 this is impossible; for larger n a
        constructive modular schedule works.

        Algorithm:
        - If n <= 4 return [].
        - Emit difference-1 matches in an interleaved home/away pattern that
          already separates teams by a day.
        - For each larger difference d < (n+1)//2, append n home-then-away
          rounds, choosing the start index from the previous match so no team
          repeats on consecutive days.
        - For even n, finish with the d = n/2 diameter round.

        Complexity: O(n^2) time and space (output size).
        """
        result: List[List[int]] = []
        if n <= 4:
            return result
        d = 1
        if n % 2 == 0:
            for i in range(0, n, 2):
                result.append([i, i + d])
            for i in range(0, n, 2):
                result.append([i + d, i])
            for i in range(1, n, 2):
                result.append([i, (i + d) % n])
            for i in range(1, n, 2):
                result.append([(i + d) % n, i])
        else:
            for i in range(0, 2 * n, 2):
                result.append([i % n, (i + d) % n])
            for i in range(0, 2 * n, 2):
                result.append([(i + d) % n, i % n])
        for d in range(2, (n + 1) // 2):
            j = result[-1][0] + 1
            for i in range(j, j + n):
                result.append([i % n, (i + d) % n])
            j = result[-1][1] - 1
            for i in range(j, j + n):
                result.append([(i + d) % n, i % n])
        if n % 2 == 0:
            d = n // 2
            j = result[-1][0] - 1
            for i in range(j, j + n):
                result.append([i % n, (i + d) % n])
        return result
# @lc code=end
