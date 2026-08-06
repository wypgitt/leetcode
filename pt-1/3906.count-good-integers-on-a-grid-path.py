#
# @lc app=leetcode id=3906 lang=python3
#
# [3906] Count Good Integers on a Grid Path
#
# https://leetcode.com/problems/count-good-integers-on-a-grid-path/description/
#
# algorithms
# Hard (49.30%)
# Likes:    60
# Dislikes: 4
# Total Accepted:    7.7K
# Total Submissions: 15.5K
# Testcase Example:  "8\n10\n\"DDDRRR\""
#
#
# You are given two integers l and r, and a string directions consisting
# of exactly three 'D' characters and three 'R' characters.
#
# For each integer x in the range [l, r] (inclusive), perform the
# following steps:
#
# If x has fewer than 16 digits, pad it on the left with leading zeros to
# obtain a 16-digit string.
#
# Place the 16 digits into a 4 × 4 grid in row-major order (the first 4
# digits form the first row from left to right, the next 4 digits form the
# second row, and so on).
#
# Starting at the top-left cell (row = 0, column = 0), apply the 6
# characters of directions in order:
#
# 'D' increments the row by 1.
#
# 'R' increments the column by 1.
#
# Record the sequence of digits visited along the path (including the
# starting cell), producing a sequence of length 7.
#
# The integer x is considered good if the recorded sequence is
# non-decreasing.
#
# Return an integer representing the number of good integers in the range
# [l, r].
#
# Example 1:
#
# Input: l = 8, r = 10, directions = "DDDRRR"
#
# Output: 2
#
# Explanation:
#
# The grid for x = 8:
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         8
#
# Path: (0,0) → (1,0) → (2,0) → (3,0) → (3,1) → (3,2) → (3,3)
#
# The sequence of digits visited is [0, 0, 0, 0, 0, 0, 8].
#
# As the sequence of digits visited is non-decreasing, 8 is a good
# integer.
#
# The grid for x = 9:
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         9
#
# The sequence of digits visited is [0, 0, 0, 0, 0, 0, 9].
#
# As the sequence of digits visited is non-decreasing, 9 is a good
# integer.
#
# The grid for x = 10:
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         1
#                         0
#
# The sequence of digits visited is [0, 0, 0, 0, 0, 1, 0].
#
# As the sequence of digits visited is not non-decreasing, 10 is not a
# good integer.
#
# Hence, only 8 and 9 are good, giving a total of 2 good integers in the
# range.
#
# Example 2:
#
# Input: l = 123456789, r = 123456790, directions = "DDRRDR"
#
# Output: 1
#
# Explanation:
#
# The grid for x = 123456789:
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         1
#
#                         2
#                         3
#                         4
#                         5
#
#                         6
#                         7
#                         8
#                         9
#
# Path: (0,0) → (1,0) → (2,0) → (2,1) → (2,2) → (3,2) → (3,3)
#
# The sequence of digits visited is [0, 0, 2, 3, 4, 8, 9].
#
# As the sequence of digits visited is non-decreasing, 123456789 is a good
# integer.
#
# The grid for x = 123456790:
#
#                         0
#                         0
#                         0
#                         0
#
#                         0
#                         0
#                         0
#                         1
#
#                         2
#                         3
#                         4
#                         5
#
#                         6
#                         7
#                         9
#                         0
#
# The sequence of digits visited is [0, 0, 2, 3, 4, 9, 0].
#
# As the sequence of digits visited is not non-decreasing, 123456790 is
# not a good integer.
#
# Hence, only 123456789 is good, giving a total of 1 good integer in the
# range.
#
# Example 3:
#
# Input: l = 1288561398769758, r = 1288561398769758, directions = "RRRDDD"
#
# Output: 0
#
# Explanation:
#
# The grid for x = 1288561398769758:
#
#                         1
#                         2
#                         8
#                         8
#
#                         5
#                         6
#                         1
#                         3
#
#                         9
#                         8
#                         7
#                         6
#
#                         9
#                         7
#                         5
#                         8
#
# Path: (0,0) → (0,1) → (0,2) → (0,3) → (1,3) → (2,3) → (3,3)
#
# The sequence of digits visited is [1, 2, 8, 8, 3, 6, 8].
#
# ​​​​​​​As the sequence of digits visited is not non-decreasing,
# 1288561398769758 is not a good integer.
#
# No numbers are good, giving a total of 0 good integers in the range.
#
# Constraints:
#
# 1 <= l <= r <= 9 × 10^15
#
# directions.length == 6
#
# directions consists of exactly three 'D' characters and three 'R'
# characters.
#

# @lc code=start
class Solution:
    def countGoodIntegersOnPath(self, l: int, r: int, directions: str) -> int:
        """
        Interview explanation:
        Pad each x to 16 digits in a 4×4 grid; the path visits 7 cells. Count
        numbers whose path digits are non-decreasing via digit DP.

        Algorithm:
        - Mark the 7 path positions from directions (3D+3R from (0,0)).
        - Digit DP over 16 positions: when on-path, require digit ≥ previous
          path digit; off-path digits are free (tight bound only).
        - Answer = count(r) − count(l−1).

        Complexity: O(16 · 2 · 10^2) per bound.
        """
        L = 16
        on_path = [False] * L
        i = j = 0
        on_path[0] = True
        for ch in directions:
            if ch == 'D':
                i += 1
            else:
                j += 1
            on_path[i * 4 + j] = True

        def count(n: int) -> int:
            if n < 0:
                return 0
            digits = [0] * L
            x = n
            for pos in range(L - 1, -1, -1):
                digits[pos] = x % 10
                x //= 10
            # dp[tight][last_path_digit]
            dp = [[0] * 10 for _ in range(2)]
            dp[1][0] = 1
            for pos in range(L):
                new_dp = [[0] * 10 for _ in range(2)]
                for tight in range(2):
                    bound = digits[pos] if tight else 9
                    for last in range(10):
                        if not dp[tight][last]:
                            continue
                        for d in range(bound + 1):
                            nlast = last
                            if on_path[pos]:
                                if d < last:
                                    continue
                                nlast = d
                            nt = tight and d == bound
                            new_dp[nt][nlast] += dp[tight][last]
                dp = new_dp
            return sum(sum(row) for row in dp)

        return count(r) - count(l - 1)
# @lc code=end
