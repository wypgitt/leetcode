#
# @lc app=leetcode id=3921 lang=python3
#
# [3921] Score Validator
#
# https://leetcode.com/problems/score-validator/description/
#
# algorithms
# Easy (73.71%)
# Likes:    21
# Dislikes: 2
# Total Accepted:    37.3K
# Total Submissions: 50.6K
# Testcase Example:  "[\"1\",\"4\",\"W\",\"6\",\"WD\"]"
#
#
# You are given a string array events.
#
# Initially, score = 0 and counter = 0. Each element in events is one of
# the following:
#
# "0", "1", "2", "3", "4", "6": Add that value to the total score.
#
# "W": Increase the counter by 1. No score is added.
#
# "WD": Add 1 to the total score.
#
# "NB": Add 1 to the total score.
#
# Process the array from left to right. Stop processing when either:
#
# All elements in events have been processed, or
#
# The counter becomes 10.
#
# Return an integer array [score, counter], where:
#
# score is the final total score.
#
# counter is the final counter value.
#
# Example 1:
#
# Input: events = ["1","4","W","6","WD"]
#
# Output: [12,1]
#
# Explanation:
#
#                         Event
#                         Score
#                         Counter
#
#                         "1"
#                         1
#                         0
#
#                         "4"
#                         5
#                         0
#
#                         "W"
#                         5
#                         1
#
#                         "6"
#                         11
#                         1
#
#                         "WD"
#                         12
#                         1
#
# Final result: [12, 1].
#
# Example 2:
#
# Input: events = ["WD","NB","0","4","4"]
#
# Output: [10,0]
#
# Explanation:
#
#                         Event
#                         Score
#                         Counter
#
#                         "WD"
#                         1
#                         0
#
#                         "NB"
#                         2
#                         0
#
#                         "0"
#                         2
#                         0
#
#                         "4"
#                         6
#                         0
#
#                         "4"
#                         10
#                         0
#
# Final result: [10, 0].
#
# Example 3:
#
# Input: events = ["W","W","W","W","W","W","W","W","W","W","W"]
#
# Output: [0,10]
#
# Explanation:
#
# After 10 occurrences of "W", the counter reaches 10, so processing
# stops. The remaining events are ignored.
#
# Constraints:
#
# 1 <= events.length <= 1000
#
# events[i] is one of "0", "1", "2", "3", "4", "6", "W", "WD", or "NB".
#

# @lc code=start
class Solution:
    def scoreValidator(self, events: list[str]) -> list[int]:
        """
        Interview explanation:
        Simulate cricket-like scoring events until 10 wickets ("W") or the end.

        Algorithm:
        - Digits add their value; WD/NB add 1; W increments counter.
        - Stop when counter hits 10; return [score, counter].

        Complexity: O(n) time, O(1) space.
        """
        score = counter = 0
        for e in events:
            if counter == 10:
                break
            if e == "W":
                counter += 1
            elif e in ("WD", "NB"):
                score += 1
            else:
                score += int(e)
        return [score, counter]
# @lc code=end
