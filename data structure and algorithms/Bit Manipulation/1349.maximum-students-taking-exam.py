#
# @lc app=leetcode id=1349 lang=python3
#
# [1349] Maximum Students Taking Exam
#
# https://leetcode.com/problems/maximum-students-taking-exam/description/
#
# algorithms
# Hard (54.23%)
# Likes:    913
# Dislikes: 20
# Total Accepted:    24.8K
# Total Submissions: 45.8K
# Testcase Example:  "[[\"#\",\".\",\"#\",\"#\",\".\",\"#\"],[\".\",\"#\",\"#\",\"#\",\"#\",\".\"],[\"#\",\".\",\"#\",\"#\",\".\",\"#\"]]"
#
# Given a m * n matrix seats that represent seats distributions in a classroom.
# If a seat is broken, it is denoted by '#' character otherwise it is denoted
# by a '.' character.
#
# Students can see the answers of those sitting next to the left, right, upper
# left and upper right, but he cannot see the answers of the student sitting
# directly in front or behind him. Return the maximum number of students that
# can take the exam together without any cheating being possible.
#
# Students must be placed in seats in good condition.
#
# Example 1:
#
# Input: seats = [["#",".","#","#",".","#"],
# [".","#","#","#","#","."],
# ["#",".","#","#",".","#"]]
# Output: 4
# Explanation: Teacher can place 4 students in available seats so they don't
# cheat on the exam.
#
# Example 2:
#
# Input: seats = [[".","#"],
# ["#","#"],
# ["#","."],
# ["#","#"],
# [".","#"]]
# Output: 3
# Explanation: Place all students in available seats.
#
# Example 3:
#
# Input: seats = [["#",".",".",".","#"],
# [".","#",".","#","."],
# [".",".","#",".","."],
# [".","#",".","#","."],
# ["#",".",".",".","#"]]
# Output: 10
# Explanation: Place students in available seats in column 1, 3 and 5.
#
# Constraints:
#
# seats contains only characters '.' and'#'.
#
# m == seats.length
#
# n == seats[i].length
#
# 1 <= m <= 8
#
# 1 <= n <= 8
#

# @lc code=start
from typing import List


class Solution:
    def maxStudents(self, seats: List[List[str]]) -> int:
        """
        Interview explanation:
        Seat students so no two can cheat: no left/right adjacent in same row,
        and no diagonal adjacent to previous row. Rows as bitmasks; DP over
        row index and previous mask.

        Algorithm (DP bitmask):
        - For each row list valid masks (bits only on '.', no adjacent 1s).
        - dp[r][mask] = max students; transition if no diagonal conflict with
          prev mask: (mask & (prev<<1))==0 and (mask & (prev>>1))==0.

        Complexity: O(m * 4^n) roughly with n=cols<=8, O(m * 2^n) space.
        """
        m, n = len(seats), len(seats[0])
        # seat bit: 1 means available originally; we'll place on available
        row_bits = []
        for r in range(m):
            bits = 0
            for c in range(n):
                if seats[r][c] == ".":
                    bits |= 1 << c
            row_bits.append(bits)

        def ok(mask: int, seats_bits: int) -> bool:
            if mask & ~seats_bits:
                return False
            # no adjacent students
            return (mask & (mask << 1)) == 0

        # valid masks per row
        valids = []
        for rb in row_bits:
            cur = []
            for mask in range(1 << n):
                if ok(mask, rb):
                    cur.append(mask)
            valids.append(cur)

        # dp: map mask -> best for current row processing
        dp = {0: 0}  # before row 0, prev mask 0
        for r in range(m):
            ndp = {}
            for prev, best in dp.items():
                for mask in valids[r]:
                    if (mask & (prev << 1)) or (mask & (prev >> 1)):
                        continue
                    ndp[mask] = max(ndp.get(mask, 0), best + bin(mask).count("1"))
            dp = ndp
        return max(dp.values()) if dp else 0
# @lc code=end

