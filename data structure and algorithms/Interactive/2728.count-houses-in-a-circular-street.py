#
# @lc app=leetcode id=2728 lang=python3
#
# [2728] Count Houses in a Circular Street
#
# https://leetcode.com/problems/count-houses-in-a-circular-street/description/
#
# algorithms
# Easy (86.02%)
# Likes:    61
# Dislikes: 12
# Total Accepted:    3.5K
# Total Submissions: 4K
# Testcase Example:  "[0,0,0,0]\n10"
#
#
# You are given an object street of class Street that represents a
# circular street and a positive integer k which represents a maximum
# bound for the number of houses in that street (in other words, the
# number of houses is less than or equal to k). Houses' doors could be
# open or closed initially.
#
# Initially, you are standing in front of a door to a house on this
# street. Your task is to count the number of houses in the street.
#
# The class Street contains the following functions which may help you:
#
# void openDoor(): Open the door of the house you are in front of.
#
# void closeDoor(): Close the door of the house you are in front of.
#
# boolean isDoorOpen(): Returns true if the door of the current house is
# open and false otherwise.
#
# void moveRight(): Move to the right house.
#
# void moveLeft(): Move to the left house.
#
# Return ans which represents the number of houses on this street.
#
# Example 1:
#
# Input: street = [0,0,0,0], k = 10
# Output: 4
# Explanation: There are 4 houses, and all their doors are closed.
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
# 1 <= n <= k <= 10^3
#
# @lc code=start
from typing import Optional

# Definition for a street.
# class Street:
#     def openDoor(self):
#         pass
#     def closeDoor(self):
#         pass
#     def isDoorOpen(self):
#         pass
#     def moveRight(self):
#         pass
#     def moveLeft(self):
#         pass


try:
    Street  # type: ignore[name-defined]
except NameError:

    class Street:  # type: ignore[no-redef]
        def openDoor(self) -> None:
            """
            Interview explanation:
            External API stub: open current door.

            Algorithm:
            - No-op stub for local compile.

            Complexity: O(1).
            """
            return None

        def closeDoor(self) -> None:
            """
            Interview explanation:
            External API stub: close current door.

            Algorithm:
            - No-op stub for local compile.

            Complexity: O(1).
            """
            return None

        def isDoorOpen(self) -> bool:
            """
            Interview explanation:
            External API stub: whether current door is open.

            Algorithm:
            - Return False stub.

            Complexity: O(1).
            """
            return False

        def moveRight(self) -> None:
            """
            Interview explanation:
            External API stub: step to the right house.

            Algorithm:
            - No-op stub for local compile.

            Complexity: O(1).
            """
            return None

        def moveLeft(self) -> None:
            """
            Interview explanation:
            External API stub: step to the left house.

            Algorithm:
            - No-op stub for local compile.

            Complexity: O(1).
            """
            return None


class Solution:
    def houseCount(self, street: Optional["Street"], k: int) -> int:
        """
        Interview explanation:
        Premium interactive. Circular street with <= k houses; count houses via door API.

        Algorithm:
        - Open doors while walking k steps (mark all); then walk closing until a closed
          door (unmarked) — steps taken equals house count.

        Complexity: O(k) API calls, O(1) space.
        """
        for _ in range(k):
            street.openDoor()
            street.moveLeft()
        ans = 0
        while street.isDoorOpen():
            street.closeDoor()
            street.moveLeft()
            ans += 1
        return ans
# @lc code=end
