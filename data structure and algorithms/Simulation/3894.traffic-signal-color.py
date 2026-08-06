#
# @lc app=leetcode id=3894 lang=python3
#
# [3894] Traffic Signal Color
#
# https://leetcode.com/problems/traffic-signal-color/description/
#
# algorithms
# Easy (83.86%)
# Likes:    32
# Dislikes: 9
# Total Accepted:    50K
# Total Submissions: 59.6K
# Testcase Example:  "60"
#
#
# You are given an integer timer representing the remaining time (in
# seconds) on a traffic signal.
#
# The signal follows these rules:
#
# If timer == 0, the signal is "Green"
#
# If timer == 30, the signal is "Orange"
#
# If 30 < timer <= 90, the signal is "Red"
#
# Return the current state of the signal. If none of the above conditions
# are met, return "Invalid".
#
# Example 1:
#
# Input: timer = 60
#
# Output: "Red"
#
# Explanation:
#
# Since timer = 60, and 30 < timer <= 90, the answer is "Red".
#
# Example 2:
#
# Input: timer = 5
#
# Output: "Invalid"
#
# Explanation:
#
# Since timer = 5, it does not satisfy any of the given conditions, the
# answer is "Invalid".
#
# Constraints:
#
# 0 <= timer <= 1000
#

# @lc code=start
class Solution:
    def trafficSignal(self, timer: int) -> str:
        """
        Interview explanation:
        Map timer to Green / Orange / Red by the given thresholds; else Invalid.

        Algorithm:
        - 0 → Green; 30 → Orange; (30,90] → Red; otherwise Invalid.

        Complexity: O(1) time, O(1) space.
        """
        if timer == 0:
            return "Green"
        if timer == 30:
            return "Orange"
        if 30 < timer <= 90:
            return "Red"
        return "Invalid"
# @lc code=end
