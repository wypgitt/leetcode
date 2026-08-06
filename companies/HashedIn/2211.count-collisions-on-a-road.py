#
# @lc app=leetcode id=2211 lang=python3
#
# [2211] Count Collisions on a Road
#
# https://leetcode.com/problems/count-collisions-on-a-road/description/
#
# algorithms
# Medium (58.07%)
# Likes:    1130
# Dislikes: 277
# Total Accepted:    131.4K
# Total Submissions: 226.3K
# Testcase Example:  "\"RLRSLL\""
#
# There are n cars on an infinitely long road. The cars are numbered from 0 to n
# - 1 from left to right and each car is present at a unique point.
#
# You are given a 0-indexed string directions of length n. directions[i] can be
# either 'L', 'R', or 'S' denoting whether the i^th car is moving towards the
# left, towards the right, or staying at its current point respectively. Each
# moving car has the same speed.
#
# The number of collisions can be calculated as follows:
#
#
# When two cars moving in opposite directions collide with each other, the
# number of collisions increases by 2.
#
#
# When a moving car collides with a stationary car, the number of collisions
# increases by 1.
#
# After a collision, the cars involved can no longer move and will stay at the
# point where they collided. Other than that, cars cannot change their state or
# direction of motion.
#
# Return the total number of collisions that will happen on the road.
#
#
#
# Example 1:
#
# Input: directions = "RLRSLL"
# Output: 5
# Explanation:
# The collisions that will happen on the road are:
# - Cars 0 and 1 will collide with each other. Since they are moving in opposite
# directions, the number of collisions becomes 0 + 2 = 2.
# - Cars 2 and 3 will collide with each other. Since car 3 is stationary, the
# number of collisions becomes 2 + 1 = 3.
# - Cars 3 and 4 will collide with each other. Since car 3 is stationary, the
# number of collisions becomes 3 + 1 = 4.
# - Cars 4 and 5 will collide with each other. After car 4 collides with car 3,
# it will stay at the point of collision and get hit by car 5. The number of
# collisions becomes 4 + 1 = 5.
# Thus, the total number of collisions that will happen on the road is 5.
#
# Example 2:
#
# Input: directions = "LLRR"
# Output: 0
# Explanation:
# No cars will collide with each other. Thus, the total number of collisions
# that will happen on the road is 0.
#
#
#
# Constraints:
#
#
# 1 <= directions.length <= 10^5
#
#
# directions[i] is either 'L', 'R', or 'S'.
#

# @lc code=start
class Solution:
    def countCollisions(self, directions: str) -> int:
        """
        Interview explanation:
        Cars R/L/S collide until only a prefix of L and suffix of R remain moving
        away. Count collisions among the rest.

        Algorithm:
        - Strip leading L and trailing R; remaining non-S cars each collide once.

        Complexity: O(n) time, O(n) space.
        """
        s = directions.lstrip("L").rstrip("R")
        return len(s) - s.count("S")

    def countCollisions_math(self, directions: str) -> int:
        """
        Interview explanation:
        Alternate closed form: n - leading_L_count - trailing_R_count - already_S
        in the middle equals collisions; same as strip formula.

        Algorithm:
        - Find first non-L and last non-R; count non-S in between.

        Complexity: O(n) time, O(1) space.
        """
        n = len(directions)
        i, j = 0, n - 1
        while i < n and directions[i] == "L":
            i += 1
        while j >= 0 and directions[j] == "R":
            j -= 1
        if i > j:
            return 0
        return sum(1 for k in range(i, j + 1) if directions[k] != "S")
# @lc code=end
