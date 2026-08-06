#
# @lc app=leetcode id=964 lang=python3
#
# [964] Least Operators to Express Number
#
# https://leetcode.com/problems/least-operators-to-express-number/description/
#
# algorithms
# Hard (48.42%)
# Likes:    331
# Dislikes: 71
# Total Accepted:    13.2K
# Total Submissions: 27.3K
# Testcase Example:  "3"
#
# Given a single positive integer x, we will write an expression of the form x
# (op1) x (op2) x (op3) x ... where each operator op1, op2, etc. is either
# addition, subtraction, multiplication, or division (+, -, *, or /). For
# example, with x = 3, we might write 3 * 3 / 3 + 3 - 3 which is a value of 3.
#
# When writing such an expression, we adhere to the following conventions:
#
# The division operator (/) returns rational numbers.
#
# There are no parentheses placed anywhere.
#
# We use the usual order of operations: multiplication and division happen
# before addition and subtraction.
#
# It is not allowed to use the unary negation operator (-). For example, "x -
# x" is a valid expression as it only uses subtraction, but "-x + x" is not
# because it uses negation.
#
# We would like to write an expression with the least number of operators such
# that the expression equals the given target. Return the least number of
# operators used.
#
# Example 1:
#
# Input: x = 3, target = 19
# Output: 5
# Explanation: 3 * 3 + 3 * 3 + 3 / 3.
# The expression contains 5 operations.
#
# Example 2:
#
# Input: x = 5, target = 501
# Output: 8
# Explanation: 5 * 5 * 5 * 5 - 5 * 5 * 5 + 5 / 5.
# The expression contains 8 operations.
#
# Example 3:
#
# Input: x = 100, target = 100000000
# Output: 3
# Explanation: 100 * 100 * 100 * 100.
# The expression contains 3 operations.
#
# Constraints:
#
# 2 <= x <= 100
#
# 1 <= target <= 2 * 10^8
#

# @lc code=start
class Solution:
    def leastOpsExpressTarget(self, x: int, target: int) -> int:
        """
        Interview explanation:
        Express target using only x with +,-,*,/ ; minimize operator count.
        Process target in base-x digits from low to high: at digit position k,
        track costs to reach the current residue (pos) or the complement to the
        next power (neg); combine with the next digit.

        Algorithm (base-x digit DP):
        - pos/neg = ops to make cur residue / (x^k - residue) at power k
        - For each remainder r = target % x (then target //= x):
          - k==0: pos=2r, neg=2(x-r)  # via ± (x/x) forms
          - else: update pos/neg from r*k + previous options
        - Return min(pos, k+neg) - 1  # subtract the unused leading '+'

        Complexity: O(log_x target) time, O(1) space.
        """
        pos = neg = k = 0
        while target:
            target, r = divmod(target, x)
            if k > 0:
                pos, neg = (
                    min(r * k + pos, (r + 1) * k + neg),
                    min((x - r) * k + pos, (x - r - 1) * k + neg),
                )
            else:
                pos, neg = r * 2, (x - r) * 2
            k += 1
        return min(pos, k + neg) - 1
# @lc code=end



