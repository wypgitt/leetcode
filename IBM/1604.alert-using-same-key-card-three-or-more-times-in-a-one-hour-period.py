#
# @lc app=leetcode id=1604 lang=python3
#
# [1604] Alert Using Same Key-Card Three or More Times in a One Hour Period
#
# https://leetcode.com/problems/alert-using-same-key-card-three-or-more-times-in-a-one-hour-period/description/
#
# algorithms
# Medium (46.35%)
# Likes:    340
# Dislikes: 441
# Total Accepted:    51.2K
# Total Submissions: 110K
# Testcase Example:  "[\"daniel\",\"daniel\",\"daniel\",\"luis\",\"luis\",\"luis\",\"luis\"]"
#
# LeetCode company workers use key-cards to unlock office doors. Each time a
# worker uses their key-card, the security system saves the worker's name and
# the time when it was used. The system emits an alert if any worker uses the
# key-card three or more times in a one-hour period.
#
# You are given a list of strings keyName and keyTime where [keyName[i],
# keyTime[i]] corresponds to a person's name and the time when their key-card
# was used in a single day.
#
# Access times are given in the 24-hour time format "HH:MM", such as "23:51"
# and "09:49".
#
# Return a list of unique worker names who received an alert for frequent
# keycard use. Sort the names in ascending order alphabetically.
#
# Notice that "10:00" - "11:00" is considered to be within a one-hour period,
# while "22:51" - "23:52" is not considered to be within a one-hour period.
#
# Example 1:
#
# Input: keyName = ["daniel","daniel","daniel","luis","luis","luis","luis"],
# keyTime = ["10:00","10:40","11:00","09:00","11:00","13:00","15:00"]
# Output: ["daniel"]
# Explanation: "daniel" used the keycard 3 times in a one-hour period
# ("10:00","10:40", "11:00").
#
# Example 2:
#
# Input: keyName = ["alice","alice","alice","bob","bob","bob","bob"], keyTime =
# ["12:01","12:00","18:00","21:00","21:20","21:30","23:00"]
# Output: ["bob"]
# Explanation: "bob" used the keycard 3 times in a one-hour period
# ("21:00","21:20", "21:30").
#
# Constraints:
#
# 1 <= keyName.length, keyTime.length <= 10^5
#
# keyName.length == keyTime.length
#
# keyTime[i] is in the format "HH:MM".
#
# [keyName[i], keyTime[i]] is unique.
#
# 1 <= keyName[i].length <= 10
#
# keyName[i] contains only lowercase English letters.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def alertNames(self, keyName: List[str], keyTime: List[str]) -> List[str]:
        """
        Interview explanation:
        Alert if a person uses keycard >=3 times within any 60-minute window.
        Group times by name, sort, then sliding window of size 3.

        Algorithm (sort + window):
        - Parse HH:MM to minutes; map name -> list of times; sort each list.
        - For each name, if any times[i+2] - times[i] <= 60, alert.
        - Return sorted alert names.

        Complexity: O(n log n) time, O(n) space.
        """
        def to_min(t: str) -> int:
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        times = defaultdict(list)
        for name, t in zip(keyName, keyTime):
            times[name].append(to_min(t))
        ans = []
        for name, arr in times.items():
            arr.sort()
            for i in range(len(arr) - 2):
                if arr[i + 2] - arr[i] <= 60:
                    ans.append(name)
                    break
        ans.sort()
        return ans

    def alertNames_twopointer(self, keyName: List[str], keyTime: List[str]) -> List[str]:
        """
        Interview explanation:
        Same grouping; two-pointer expanding window counting uses in 60 minutes.

        Algorithm (two pointers):
        - Sort times; left=0; for right, advance left while times[right]-times[left]>60;
          if right-left+1 >= 3 alert.

        Complexity: O(n log n) time, O(n) space.
        """
        def to_min(t: str) -> int:
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        times = defaultdict(list)
        for name, t in zip(keyName, keyTime):
            times[name].append(to_min(t))
        ans = []
        for name, arr in times.items():
            arr.sort()
            left = 0
            for right in range(len(arr)):
                while arr[right] - arr[left] > 60:
                    left += 1
                if right - left + 1 >= 3:
                    ans.append(name)
                    break
        ans.sort()
        return ans
# @lc code=end
