#
# @lc app=leetcode id=640 lang=python3
#
# [640] Solve the Equation
#
# https://leetcode.com/problems/solve-the-equation/description/
#
# algorithms
# Medium (46.15%)
# Likes:    551
# Dislikes: 854
# Total Accepted:    51.1K
# Total Submissions: 110.7K
# Testcase Example:  '"x+5-3+x=6+x-2"'
#
# Solve a given equation and return the value of 'x' in the form of a string
# "x=#value". The equation contains only '+', '-' operation, the variable 'x'
# and its coefficient. You should return "No solution" if there is no solution
# for the equation, or "Infinite solutions" if there are infinite solutions for
# the equation.
# 
# If there is exactly one solution for the equation, we ensure that the value
# of 'x' is an integer.
# 
# 
# Example 1:
# 
# 
# Input: equation = "x+5-3+x=6+x-2"
# Output: "x=2"
# 
# 
# Example 2:
# 
# 
# Input: equation = "x=x"
# Output: "Infinite solutions"
# 
# 
# Example 3:
# 
# 
# Input: equation = "2x=x"
# Output: "x=0"
# 
# 
# 
# Constraints:
# 
# 
# 3 <= equation.length <= 1000
# equation has exactly one '='.
# equation consists of integers with an absolute value in the range [0, 100]
# without any leading zeros, and the variable 'x'.
# The input is generated that if there is a single solution, it will be an
# integer.
# 
# 
#

# @lc code=start
class Solution:
    def solveEquation(self, equation: str) -> str:
        def parse(side: str) -> tuple[int, int]:
            coeff = const = 0
            i = 0
            sign = 1
            while i < len(side):
                if side[i] == '+':
                    sign = 1
                    i += 1
                elif side[i] == '-':
                    sign = -1
                    i += 1
                else:
                    j = i
                    while j < len(side) and side[j].isdigit():
                        j += 1
                    num = int(side[i:j]) if j > i else 1
                    if j < len(side) and side[j] == 'x':
                        coeff += sign * num
                        j += 1
                    else:
                        const += sign * num
                    i = j
            return coeff, const

        left, right = equation.split('=')
        lx, lc = parse(left)
        rx, rc = parse(right)
        coeff = lx - rx
        const = rc - lc
        if coeff == 0:
            return 'Infinite solutions' if const == 0 else 'No solution'
        return f"x={const // coeff}"
# @lc code=end

"""
Interview explanation:
Parse each side into coeff*x + constant. Moving x terms to the left and constants to the right gives coeff*x = const. Then solve, or detect zero-coefficient cases.

Data structure: scalar counters for x coefficient and constant. Manual parsing handles implicit coefficients such as x and -x.

Edge cases: coeff=0 with const=0 means both sides are identical; coeff=0 with nonzero const is impossible. Integer division is safe because the problem guarantees an integer solution when unique.

Complexity: O(n) time to scan the equation and O(1) space.
"""
