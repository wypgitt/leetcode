#
# @lc app=leetcode id=3027 lang=python3
#
# [3027] Find the Number of Ways to Place People II
#
# https://leetcode.com/problems/find-the-number-of-ways-to-place-people-ii/description/
#
# algorithms
# Hard (64.18%)
# Likes:    358
# Dislikes: 64
# Total Accepted:    88.9K
# Total Submissions: 138.5K
# Testcase Example:  "[[1,1],[2,2],[3,3]]"
#
#
# You are given a 2D array points of size n x 2 representing integer
# coordinates of some points on a 2D-plane, where points[i] = [x_i, y_i].
#
# We define the right direction as positive x-axis (increasing
# x-coordinate) and the left direction as negative x-axis (decreasing
# x-coordinate). Similarly, we define the up direction as positive y-axis
# (increasing y-coordinate) and the down direction as negative y-axis
# (decreasing y-coordinate)
#
# You have to place n people, including Alice and Bob, at these points
# such that there is exactly one person at every point. Alice wants to be
# alone with Bob, so Alice will build a rectangular fence with Alice's
# position as the upper left corner and Bob's position as the lower right
# corner of the fence (Note that the fence might not enclose any area,
# i.e. it can be a line). If any person other than Alice and Bob is either
# inside the fence or on the fence, Alice will be sad.
#
# Return the number of pairs of points where you can place Alice and Bob,
# such that Alice does not become sad on building the fence.
#
# Note that Alice can only build a fence with Alice's position as the
# upper left corner, and Bob's position as the lower right corner. For
# example, Alice cannot build either of the fences in the picture below
# with four corners (1, 1), (1, 3), (3, 1), and (3, 3), because:
#
# With Alice at (3, 3) and Bob at (1, 1), Alice's position is not the
# upper left corner and Bob's position is not the lower right corner of
# the fence.
#
# With Alice at (1, 3) and Bob at (1, 1) (as the rectangle shown in the
# image instead of a line), Bob's position is not the lower right corner
# of the fence.
#
# Example 1:
#
# Input: points = [[1,1],[2,2],[3,3]]
# Output: 0
# Explanation: There is no way to place Alice and Bob such that Alice can
# build a fence with Alice's position as the upper left corner and Bob's
# position as the lower right corner. Hence we return 0.
#
# Example 2:
#
# Input: points = [[6,2],[4,4],[2,6]]
# Output: 2
# Explanation: There are two ways to place Alice and Bob such that Alice
# will not be sad:
# - Place Alice at (4, 4) and Bob at (6, 2).
# - Place Alice at (2, 6) and Bob at (4, 4).
# You cannot place Alice at (2, 6) and Bob at (6, 2) because the person at
# (4, 4) will be inside the fence.
#
# Example 3:
#
# Input: points = [[3,1],[1,3],[1,1]]
# Output: 2
# Explanation: There are two ways to place Alice and Bob such that Alice
# will not be sad:
# - Place Alice at (1, 1) and Bob at (3, 1).
# - Place Alice at (1, 3) and Bob at (1, 1).
# You cannot place Alice at (1, 3) and Bob at (3, 1) because the person at
# (1, 1) will be on the fence.
# Note that it does not matter if the fence encloses any area, the first
# and second fences in the image are valid.
#
# Constraints:
#
# 2 <= n <= 1000
#
# points[i].length == 2
#
# -10^9 <= points[i][0], points[i][1] <= 10^9
#
# All points[i] are distinct.
#

# @lc code=start

from typing import List


class Solution:
    def numberOfPairs(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Count Alice/Bob placements where Alice is upper-left, Bob lower-right,
        and the fence is empty. n<=1000 needs O(n^2).

        Algorithm:
        - Sort by x ascending, y descending so left-to-right scan is valid.
        - For each Alice i, scan j>i: Bob valid if yj<=yi and yj is strictly
          above all previously accepted Bob y's (else a prior point sits inside).

        Complexity: O(n^2) time, O(n) space.
        """
        pts = sorted(points, key=lambda p: (p[0], -p[1]))
        n = len(pts)
        ans = 0
        for i in range(n):
            yi = pts[i][1]
            max_y = float("-inf")
            for j in range(i + 1, n):
                yj = pts[j][1]
                if yj <= yi and yj > max_y:
                    ans += 1
                    max_y = yj
        return ans
# @lc code=end
