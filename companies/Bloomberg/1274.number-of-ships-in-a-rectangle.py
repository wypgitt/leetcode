#
# @lc app=leetcode id=1274 lang=python3
#
# [1274] Number of Ships in a Rectangle
#
# https://leetcode.com/problems/number-of-ships-in-a-rectangle/description/
#
# algorithms
# Hard (68.71%)
# Likes:    540
# Dislikes: 70
# Total Accepted:    35.4K
# Total Submissions: 51.5K
# Testcase Example:  "[[1,1],[2,2],[3,3],[5,5]]\n[4,4]\n[0,0]"
#
#
# (This problem is an interactive problem.)
#
# Each ship is located at an integer point on the sea represented by a
# cartesian plane, and each integer point may contain at most 1 ship.
#
# You have a function Sea.hasShips(topRight, bottomLeft) which takes two
# points as arguments and returns true If there is at least one ship in
# the rectangle represented by the two points, including on the boundary.
#
# Given two points: the top right and bottom left corners of a rectangle,
# return the number of ships present in that rectangle. It is guaranteed
# that there are at most 10 ships in that rectangle.
#
# Submissions making more than 400 calls to hasShips will be judged Wrong
# Answer. Also, any solutions that attempt to circumvent the judge will
# result in disqualification.
#
# Example :
#
# Input:
# ships = [[1,1],[2,2],[3,3],[5,5]], topRight = [4,4], bottomLeft = [0,0]
# Output: 3
# Explanation: From [0,0] to [4,4] we can count 3 ships within the range.
#
# Example 2:
#
# Input: ans = [[1,1],[2,2],[3,3]], topRight = [1000,1000], bottomLeft =
# [0,0]
# Output: 3
#
# Constraints:
#
# On the input ships is only given to initialize the map internally. You
# must solve this problem "blindfolded". In other words, you must find the
# answer using the given hasShips API, without knowing the ships position.
#
# 0 <= bottomLeft[0] <= topRight[0] <= 1000
#
# 0 <= bottomLeft[1] <= topRight[1] <= 1000
#
# topRight != bottomLeft
#
# @lc code=start

try:
    Point  # type: ignore[name-defined]
except NameError:

    class Point:  # type: ignore[no-redef]
        def __init__(self, x: int = 0, y: int = 0):
            self.x = x
            self.y = y


try:
    Sea  # type: ignore[name-defined]
except NameError:

    class Sea:  # type: ignore[no-redef]
        def hasShips(self, topRight: "Point", bottomLeft: "Point") -> bool:
            return False


class Solution:
    def countShips(self, sea: "Sea", topRight: "Point", bottomLeft: "Point") -> int:
        """
        Interview explanation:
        Premium. Sea.hasShips(topRight, bottomLeft) reports whether any ship
        exists in the axis-aligned rectangle (inclusive). At most 10 ships.
        Divide-and-conquer: if no ships or invalid rect return 0; if single
        cell return 1; else split into 4 quadrants and sum.

        Algorithm:
        - If x1>x2 or y1>y2 or not hasShips: return 0.
        - If x1==x2 and y1==y2: return 1.
        - midX=(x1+x2)//2; midY=(y1+y2)//2; recurse 4 sub-rectangles.

        Complexity: O(S log W log H) hasShips calls with S<=10 ships.
        """
        def solve(x1: int, y1: int, x2: int, y2: int) -> int:
            if x1 > x2 or y1 > y2:
                return 0
            if not sea.hasShips(Point(x2, y2), Point(x1, y1)):
                return 0
            if x1 == x2 and y1 == y2:
                return 1
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2
            return (
                solve(x1, y1, mx, my)
                + solve(mx + 1, y1, x2, my)
                + solve(x1, my + 1, mx, y2)
                + solve(mx + 1, my + 1, x2, y2)
            )

        return solve(bottomLeft.x, bottomLeft.y, topRight.x, topRight.y)
# @lc code=end
