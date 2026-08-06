#
# @lc app=leetcode id=657 lang=python3
#
# [657] Robot Return to Origin
#
# https://leetcode.com/problems/robot-return-to-origin/description/
#
# algorithms
# Easy (78.17%)
# Likes:    2826
# Dislikes: 756
# Total Accepted:    694K
# Total Submissions: 888K
# Testcase Example:  "\"UD\""
#
# There is a robot starting at the position (0, 0), the origin, on a 2D plane.
# Given a sequence of its moves, judge if this robot ends up at (0, 0) after it
# completes its moves.
#
# You are given a string moves that represents the move sequence of the robot
# where moves[i] represents its i^th move. Valid moves are 'R' (right), 'L'
# (left), 'U' (up), and 'D' (down).
#
# Return true if the robot returns to the origin after it finishes all of its
# moves, or false otherwise.
#
# Note: The way that the robot is "facing" is irrelevant. 'R' will always make
# the robot move to the right once, 'L' will always make it move left, etc.
# Also, assume that the magnitude of the robot's movement is the same for each
# move.
#
# Example 1:
#
# Input: moves = "UD"
# Output: true
# Explanation: The robot moves up once, and then down once. All moves have the
# same magnitude, so it ended up at the origin where it started. Therefore, we
# return true.
#
# Example 2:
#
# Input: moves = "LL"
# Output: false
# Explanation: The robot moves left twice. It ends up two "moves" to the left
# of the origin. We return false because it is not at the origin at the end of
# its moves.
#
# Constraints:
#
# 1 <= moves.length <= 2 * 10^4
#
# moves only contains the characters 'U', 'D', 'L' and 'R'.
#

# @lc code=start

class Solution:
    def judgeCircle(self, moves: str) -> bool:
        """
        Interview explanation:
        Robot returns to origin iff #U==#D and #L==#R (net displacement zero).

        Algorithm:
        - Count moves or track x,y deltas; return x==0 and y==0.

        Complexity: O(N) time, O(1) space.
        """
        x = y = 0
        for m in moves:
            if m == "U":
                y += 1
            elif m == "D":
                y -= 1
            elif m == "L":
                x -= 1
            else:
                x += 1
        return x == 0 and y == 0
# @lc code=end
