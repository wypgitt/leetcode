#
# @lc app=leetcode id=1826 lang=python3
#
# [1826] Faulty Sensor
#
# https://leetcode.com/problems/faulty-sensor/description/
#
# algorithms
# Easy (50.53%)
# Likes:    72
# Dislikes: 85
# Total Accepted:    7.1K
# Total Submissions: 14.1K
# Testcase Example:  "[2,3,4,5]\n[2,1,3,4]"
#
#
# An experiment is being conducted in a lab. To ensure accuracy, there are
# two sensors collecting data simultaneously. You are given two arrays
# sensor1 and sensor2, where sensor1[i] and sensor2[i] are the i^th data
# points collected by the two sensors.
#
# However, this type of sensor has a chance of being defective, which
# causes exactly one data point to be dropped. After the data is dropped,
# all the data points to the right of the dropped data are shifted one
# place to the left, and the last data point is replaced with some random
# value. It is guaranteed that this random value will not be equal to the
# dropped value.
#
# For example, if the correct data is [1,2,3,4,5] and 3 is dropped, the
# sensor could return [1,2,4,5,7] (the last position can be any value, not
# just 7).
#
# We know that there is a defect in at most one of the sensors. Return the
# sensor number (1 or 2) with the defect. If there is no defect in either
# sensor or if it is impossible to determine the defective sensor, return
# -1.
#
# Example 1:
#
# Input: sensor1 = [2,3,4,5], sensor2 = [2,1,3,4]
# Output: 1
# Explanation: Sensor 2 has the correct values.
# The second data point from sensor 2 is dropped, and the last value of
# sensor 1 is replaced by a 5.
#
# Example 2:
#
# Input: sensor1 = [2,2,2,2,2], sensor2 = [2,2,2,2,5]
# Output: -1
# Explanation: It is impossible to determine which sensor has a defect.
# Dropping the last value for either sensor could produce the output for
# the other sensor.
#
# Example 3:
#
# Input: sensor1 = [2,3,2,2,3,2], sensor2 = [2,3,2,3,2,7]
# Output: 2
# Explanation: Sensor 1 has the correct values.
# The fourth data point from sensor 1 is dropped, and the last value of
# sensor 1 is replaced by a 7.
#
# Constraints:
#
# sensor1.length == sensor2.length
#
# 1 <= sensor1.length <= 100
#
# 1 <= sensor1[i], sensor2[i] <= 100
#
# @lc code=start
from typing import List


class Solution:
    def badSensor(self, sensor1: List[int], sensor2: List[int]) -> int:
        """
        Interview explanation:
        Premium: two sensors; exactly one is faulty and dropped one value
        (remaining is a subsequence by dropping one). Identify which, or -1
        if ambiguous/impossible.

        Algorithm (scan first mismatch):
        - Find first i where sensor1[i]!=sensor2[i]. Check if sensor1[i:] equals
          sensor2[i+1:] (sensor2 dropped) or sensor2[i:] equals sensor1[i+1:]
          (sensor1 dropped). If both possible -> -1; if neither -> -1.

        Complexity: O(n) time, O(1) space.
        """
        n = len(sensor1)
        i = 0
        while i < n and sensor1[i] == sensor2[i]:
            i += 1
        if i == n:
            return -1

        def can_drop(a: List[int], b: List[int], start: int) -> bool:
            # a matches b after dropping one element from b at/after start
            # i.e. a[start:] == b[start+1:]
            j = start
            for x in range(start, n - 1):
                if a[x] != b[x + 1]:
                    return False
            return True

        # If sensor1 is bad: dropped one, so sensor2 aligns with sensor1 shifted
        # meaning sensor2[i:] == sensor1[i+1:]  -> can_drop(sensor2, sensor1, i)
        s1_bad = can_drop(sensor2, sensor1, i)
        s2_bad = can_drop(sensor1, sensor2, i)
        if s1_bad and s2_bad:
            return -1
        if s1_bad:
            return 1
        if s2_bad:
            return 2
        return -1
# @lc code=end
