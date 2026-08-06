#
# @lc app=leetcode id=539 lang=python3
#
# [539] Minimum Time Difference
#
# https://leetcode.com/problems/minimum-time-difference/description/
#
# algorithms
# Medium (62.66%)
# Likes:    2621
# Dislikes: 320
# Total Accepted:    355K
# Total Submissions: 566K
# Testcase Example:  "[\"23:59\",\"00:00\"]"
#
# Given a list of 24-hour clock time points in "HH:MM" format, return the
# minimum minutes difference between any two time-points in the list.
#
# Example 1:
#
# Input: timePoints = ["23:59","00:00"]
# Output: 1
#
# Example 2:
#
# Input: timePoints = ["00:00","23:59","00:00"]
# Output: 0
#
# Constraints:
#
# 2 <= timePoints.length <= 2 * 10^4
#
# timePoints[i] is in the format "HH:MM".
#

# @lc code=start
from typing import List
class Solution:
    def findMinDifference(self, timePoints: List[str]) -> int:
        """
        Interview explanation:
        Convert times to minutes, sort, and take min adjacent difference.
        Also compare last and first across midnight (circular).

        Algorithm:
        - minutes = 60*HH + MM; sort; min of sorted[i+1]-sorted[i] and
          1440 - (last - first).

        Complexity: O(n log n) time, O(n) space.
        """
        mins = sorted(int(t[:2]) * 60 + int(t[3:]) for t in timePoints)
        ans = 1440 - (mins[-1] - mins[0])
        for i in range(1, len(mins)):
            ans = min(ans, mins[i] - mins[i - 1])
        return ans
# @lc code=end

