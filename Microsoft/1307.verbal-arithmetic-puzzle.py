#
# @lc app=leetcode id=1307 lang=python3
#
# [1307] Verbal Arithmetic Puzzle
#
# https://leetcode.com/problems/verbal-arithmetic-puzzle/description/
#
# algorithms
# Hard (33.47%)
# Likes:    533
# Dislikes: 138
# Total Accepted:    18.1K
# Total Submissions: 54.2K
# Testcase Example:  "[\"SEND\",\"MORE\"]"
#
# Given an equation, represented by words on the left side and the result on
# the right side.
#
# You need to check if the equation is solvable under the following rules:
#
# Each character is decoded as one digit (0 - 9).
#
# No two characters can map to the same digit.
#
# Each words[i] and result are decoded as one number without leading zeros.
#
# Sum of numbers on the left side (words) will equal to the number on the right
# side (result).
#
# Return true if the equation is solvable, otherwise return false.
#
# Example 1:
#
# Input: words = ["SEND","MORE"], result = "MONEY"
# Output: true
# Explanation: Map 'S'-> 9, 'E'->5, 'N'->6, 'D'->7, 'M'->1, 'O'->0, 'R'->8,
# 'Y'->'2'
# Such that: "SEND" + "MORE" = "MONEY" , 9567 + 1085 = 10652
#
# Example 2:
#
# Input: words = ["SIX","SEVEN","SEVEN"], result = "TWENTY"
# Output: true
# Explanation: Map 'S'-> 6, 'I'->5, 'X'->0, 'E'->8, 'V'->7, 'N'->2, 'T'->1,
# 'W'->'3', 'Y'->4
# Such that: "SIX" + "SEVEN" + "SEVEN" = "TWENTY" , 650 + 68782 + 68782 =
# 138214
#
# Example 3:
#
# Input: words = ["LEET","CODE"], result = "POINT"
# Output: false
# Explanation: There is no possible mapping to satisfy the equation, so we
# return false.
# Note that two different characters cannot map to the same digit.
#
# Constraints:
#
# 2 <= words.length <= 5
#
# 1 <= words[i].length, result.length <= 7
#
# words[i], result contain only uppercase English letters.
#
# The number of different characters used in the expression is at most 10.
#

# @lc code=start
from typing import List


class Solution:
    def isSolvable(self, words: List[str], result: str) -> bool:
        """
        Interview explanation:
        Cryptarithm: map letters to distinct digits so sum(words)=result; no
        leading zeros. Column-by-column backtracking from the right with carry
        prunes early versus assigning all letters first.

        Algorithm (column backtracking):
        - Reverse strings; for each column assign digits to new letters, add
          word digits + carry, check against result digit, recurse with new carry.
        - Leading letters cannot be 0.

        Complexity: O(10^k) worst for k unique letters; pruned by columns.
        """
        words_r = [w[::-1] for w in words]
        result_r = result[::-1]
        max_len = max(max(len(w) for w in words_r), len(result_r))
        leading = {w[0] for w in words + [result] if len(w) > 1}
        assign = {}
        used = [False] * 10

        def dfs(pos: int, carry: int) -> bool:
            if pos == max_len:
                return carry == 0

            # letters appearing in this column
            col_letters = []
            for w in words_r:
                if pos < len(w):
                    col_letters.append(("add", w[pos]))
            has_res = pos < len(result_r)
            if has_res:
                col_letters.append(("res", result_r[pos]))

            unassigned = []
            seen_u = set()
            for _, ch in col_letters:
                if ch not in assign and ch not in seen_u:
                    seen_u.add(ch)
                    unassigned.append(ch)

            def go(ui: int) -> bool:
                if ui == len(unassigned):
                    total = carry
                    for kind, ch in col_letters:
                        if kind == "add":
                            total += assign[ch]
                    if has_res:
                        rd = assign[result_r[pos]]
                        if total % 10 != rd:
                            return False
                        return dfs(pos + 1, total // 10)
                    if total % 10 != 0:
                        return False
                    return dfs(pos + 1, total // 10)

                ch = unassigned[ui]
                for d in range(10):
                    if used[d]:
                        continue
                    if d == 0 and ch in leading:
                        continue
                    used[d] = True
                    assign[ch] = d
                    if go(ui + 1):
                        return True
                    del assign[ch]
                    used[d] = False
                return False

            return go(0)

        return dfs(0, 0)
# @lc code=end

