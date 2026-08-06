#
# @lc app=leetcode id=1124 lang=python3
#
# [1124] Longest Well-Performing Interval
#
# https://leetcode.com/problems/longest-well-performing-interval/description/
#
# algorithms
# Medium (38.06%)
# Likes:    1560
# Dislikes: 127
# Total Accepted:    50.1K
# Total Submissions: 132K
# Testcase Example:  "[9,9,6,0,6,6,9]"
#
# We are given hours, a list of the number of hours worked per day for a given
# employee.
#
# A day is considered to be a tiring day if and only if the number of hours
# worked is (strictly) greater than 8.
#
# A well-performing interval is an interval of days for which the number of
# tiring days is strictly larger than the number of non-tiring days.
#
# Return the length of the longest well-performing interval.
#
# Example 1:
#
# Input: hours = [9,9,6,0,6,6,9]
# Output: 3
# Explanation: The longest well-performing interval is [9,9,6].
#
# Example 2:
#
# Input: hours = [6,6,6]
# Output: 0
#
# Constraints:
#
# 1 <= hours.length <= 10^4
#
# 0 <= hours[i] <= 16
#

# @lc code=start
from typing import List, Dict


class Solution:
    def longestWPI(self, hours: List[int]) -> int:
        """
        Interview explanation:
        Well-performing interval: more tiring (>8) days than non-tiring.
        Map to +1/-1; need longest subarray with positive sum — prefix sums
        with first-seen index for each prefix.

        Algorithm (prefix):
        - score += 1 if hours[i]>8 else -1.
        - If score>0, answer is i+1.
        - Else if score-1 seen before, length i - first[score-1] is a candidate
          (any earlier prefix <= score-1 works; score-1 is the closest useful).

        Complexity: O(n) time, O(n) space.
        """
        first: Dict[int, int] = {}
        score = 0
        ans = 0
        for i, h in enumerate(hours):
            score += 1 if h > 8 else -1
            if score > 0:
                ans = i + 1
            else:
                if score not in first:
                    first[score] = i
                if score - 1 in first:
                    ans = max(ans, i - first[score - 1])
        return ans
# @lc code=end
