#
# @lc app=leetcode id=2753 lang=python3
#
# [2753] Count Houses in a Circular Street II
#
# https://leetcode.com/problems/count-houses-in-a-circular-street-ii/description/
#
# algorithms
# Hard (61.57%)
# Likes:    27
# Dislikes: 3
# Total Accepted:    982
# Total Submissions: 1.6K
# Testcase Example:  "[1,1,1,1]\n10"
#
#
# You are given an object street of class Street that represents a
# circular street and a positive integer k which represents a maximum
# bound for the number of houses in that street (in other words, the
# number of houses is less than or equal to k). Houses' doors could be
# open or closed initially (at least one is open).
#
# Initially, you are standing in front of a door to a house on this
# street. Your task is to count the number of houses in the street.
#
# The class Street contains the following functions which may help you:
#
# void closeDoor(): Close the door of the house you are in front of.
#
# boolean isDoorOpen(): Returns true if the door of the current house is
# open and false otherwise.
#
# void moveRight(): Move to the right house.
#
# Note that by circular street, we mean if you number the houses from 1 to
# n, then the right house of house_i is house_i+1 for i < n, and the right
# house of house_n is house_1.
#
# Return ans which represents the number of houses on this street.
#
# Example 1:
#
# Input: street = [1,1,1,1], k = 10
# Output: 4
# Explanation: There are 4 houses, and all their doors are open.
# The number of houses is less than k, which is 10.
#
# Example 2:
#
# Input: street = [1,0,1,1,0], k = 5
# Output: 5
# Explanation: There are 5 houses, and the doors of the 1st, 3rd, and 4th
# house (moving in the right direction) are open, and the rest are closed.
# The number of houses is equal to k, which is 5.
#
# Constraints:
#
# n == number of houses
#
# 1 <= n <= k <= 10^5
#
# street is circular by definition provided in the statement.
#
# The input is generated such that at least one of the doors is open.
#
# @lc code=start
from typing import Optional

# Definition for a street.
# class Street:
#     def closeDoor(self):
#         pass
#     def isDoorOpen(self):
#         pass
#     def moveRight(self):
#         pass


try:
    Street  # type: ignore[name-defined]
except NameError:

    class Street:  # type: ignore[no-redef]
        def closeDoor(self) -> None:
            pass

        def isDoorOpen(self) -> bool:
            return False

        def moveRight(self) -> None:
            pass


class Solution:
    def houseCount(self, street: Optional["Street"], k: int) -> int:
        """
        Interview explanation:
        Premium: circular street with at least one open door. API: closeDoor,
        isDoorOpen, moveRight. Count houses (n <= k).

        Algorithm:
        - Move right until at an open door (anchor).
        - Walk up to k steps right; whenever a door is open, record distance and
          close it. Last distance is the full circle length.

        Complexity: O(k) time, O(1) space.
        """
        while not street.isDoorOpen():
            street.moveRight()
        ans = 0
        for i in range(1, k + 1):
            street.moveRight()
            if street.isDoorOpen():
                ans = i
                street.closeDoor()
        return ans
# @lc code=end
