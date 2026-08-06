#
# @lc app=leetcode id=3386 lang=python3
#
# [3386] Button with Longest Push Time
#
# https://leetcode.com/problems/button-with-longest-push-time/description/
#
# algorithms
# Easy (41.08%)
# Likes:    80
# Dislikes: 76
# Total Accepted:    37.8K
# Total Submissions: 92K
# Testcase Example:  "[[1,2],[2,5],[3,9],[1,15]]"
#
#
# You are given a 2D array events which represents a sequence of events
# where a child pushes a series of buttons on a keyboard.
#
# Each events[i] = [index_i, time_i] indicates that the button at index
# index_i was pressed at time time_i.
#
# The array is sorted in increasing order of time.
#
# The time taken to press a button is the difference in time between
# consecutive button presses. The time for the first button is simply the
# time at which it was pressed.
#
# Return the index of the button that took the longest time to push. If
# multiple buttons have the same longest time, return the button with the
# smallest index.
#
# Example 1:
#
# Input: events = [[1,2],[2,5],[3,9],[1,15]]
#
# Output: 1
#
# Explanation:
#
# Button with index 1 is pressed at time 2.
#
# Button with index 2 is pressed at time 5, so it took 5 - 2 = 3 units of
# time.
#
# Button with index 3 is pressed at time 9, so it took 9 - 5 = 4 units of
# time.
#
# Button with index 1 is pressed again at time 15, so it took 15 - 9 = 6
# units of time.
#
# Example 2:
#
# Input: events = [[10,5],[1,7]]
#
# Output: 10
#
# Explanation:
#
# Button with index 10 is pressed at time 5.
#
# Button with index 1 is pressed at time 7, so it took 7 - 5 = 2 units of
# time.
#
# Constraints:
#
# 1 <= events.length <= 1000
#
# events[i] == [index_i, time_i]
#
# 1 <= index_i, time_i <= 10^5
#
# The input is generated such that events is sorted in increasing order of
# time_i.
#

# @lc code=start

from typing import List


class Solution:
    def buttonWithLongestTime(self, events: List[List[int]]) -> int:
        """
        Interview explanation:
        Push duration is time delta from the previous press (first press uses its
        absolute time). Track the max duration and smallest index on ties.

        Algorithm:
        - Scan events; duration = time_i - time_{i-1} (or time_0 for i=0).
        - Update answer when duration > best, or == best and index smaller.

        Complexity: O(n) time, O(1) space.
        """
        best_t = -1
        best_i = 0
        prev = 0
        for idx, t in events:
            dur = t - prev
            if dur > best_t or (dur == best_t and idx < best_i):
                best_t = dur
                best_i = idx
            prev = t
        return best_i
# @lc code=end
