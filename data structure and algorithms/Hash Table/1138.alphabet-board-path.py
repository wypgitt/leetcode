#
# @lc app=leetcode id=1138 lang=python3
#
# [1138] Alphabet Board Path
#
# https://leetcode.com/problems/alphabet-board-path/description/
#
# algorithms
# Medium (51.93%)
# Likes:    940
# Dislikes: 187
# Total Accepted:    60.6K
# Total Submissions: 117K
# Testcase Example:  "\"leet\""
#
# On an alphabet board, we start at position (0, 0), corresponding to character
# board[0][0].
#
# Here, board = ["abcde", "fghij", "klmno", "pqrst", "uvwxy", "z"], as shown in
# the diagram below.
#
# We may make the following moves:
#
# 'U' moves our position up one row, if the position exists on the board;
#
# 'D' moves our position down one row, if the position exists on the board;
#
# 'L' moves our position left one column, if the position exists on the board;
#
# 'R' moves our position right one column, if the position exists on the board;
#
# '!' adds the character board[r][c] at our current position (r, c) to the
# answer.
#
# (Here, the only positions that exist on the board are positions with letters
# on them.)
#
# Return a sequence of moves that makes our answer equal to target in the
# minimum number of moves. You may return any path that does so.
#
# Example 1:
#
# Input: target = "leet"
# Output: "DDR!UURRR!!DDD!"
#
# Example 2:
#
# Input: target = "code"
# Output: "RR!DDRR!UUL!R!"
#
# Constraints:
#
# 1 <= target.length <= 100
#
# target consists only of English lowercase letters.
#

# @lc code=start
class Solution:
    def alphabetBoardPath(self, target: str) -> str:
        """
        Interview explanation:
        Board rows a-e … u-y with z alone at (5,0). Move U/D/L/R and '!' to
        type. Order U/L before D/R so we never step off the board near z.

        Algorithm:
        - Map letter -> (r,c). Prefer moves that avoid walking off the board
          near z: move U and L first, then R and D (safe for z).

        Complexity: O(|target|) time/space for the path string.
        """
        def pos(ch: str):
            i = ord(ch) - ord("a")
            return divmod(i, 5)

        r, c = 0, 0
        res = []
        for ch in target:
            nr, nc = pos(ch)
            # Move vertical/horizontal carefully: U/L before D/R
            if nr < r:
                res.append("U" * (r - nr))
            if nc < c:
                res.append("L" * (c - nc))
            if nr > r:
                res.append("D" * (nr - r))
            if nc > c:
                res.append("R" * (nc - c))
            res.append("!")
            r, c = nr, nc
        return "".join(res)
# @lc code=end
