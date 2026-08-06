#
# @lc app=leetcode id=2726 lang=python3
#
# [2726] Calculator with Method Chaining
#
# https://leetcode.com/problems/calculator-with-method-chaining/description/
#
# algorithms
# Easy (76.88%)
# Likes:    154
# Dislikes: 22
# Total Accepted:    59K
# Total Submissions: 76.7K
# Testcase Example:  "[\"Calculator\", \"add\", \"subtract\", \"getResult\"]\n[10, 5, 7]"
#
# Design a Calculator class. The class should provide the mathematical
# operations of addition, subtraction, multiplication, division, and
# exponentiation. It should also allow consecutive operations to be performed
# using method chaining. The Calculator class constructor should accept a
# number which serves as the initial value of result.
#
# Your Calculator class should have the following methods:
#
#
# add - This method adds the given number value to the result and returns the
# updated Calculator.
#
#
# subtract - This method subtracts the given number value from the result and
# returns the updated Calculator.
#
#
# multiply - This method multiplies the result  by the given number value and
# returns the updated Calculator.
#
#
# divide - This method divides the result by the given number value and returns
# the updated Calculator. If the passed value is 0, an error "Division by zero
# is not allowed" should be thrown.
#
#
# power - This method raises the result to the power of the given number value
# and returns the updated Calculator.
#
#
# getResult - This method returns the result.
#
# Solutions within 10^-5 of the actual result are considered correct.
#
#
#
# Example 1:
#
# Input:
# actions = ["Calculator", "add", "subtract", "getResult"],
# values = [10, 5, 7]
# Output: 8
# Explanation:
# new Calculator(10).add(5).subtract(7).getResult() // 10 + 5 - 7 = 8
#
# Example 2:
#
# Input:
# actions = ["Calculator", "multiply", "power", "getResult"],
# values = [2, 5, 2]
# Output: 100
# Explanation:
# new Calculator(2).multiply(5).power(2).getResult() // (2 * 5) ^ 2 = 100
#
# Example 3:
#
# Input:
# actions = ["Calculator", "divide", "getResult"],
# values = [20, 0]
# Output: "Division by zero is not allowed"
# Explanation:
# new Calculator(20).divide(0).getResult() // 20 / 0
#
# The error should be thrown because we cannot divide by zero.
#
#
#
# Constraints:
#
#
# actions is a valid JSON array of strings
#
#
# values is a valid JSON array of numbers
#
#
# 2 <= actions.length <= 2 * 10^4
#
#
# 1 <= values.length <= 2 * 10^4 - 1
#
#
# actions[i] is one of "Calculator", "add", "subtract", "multiply", "divide",
# "power", and "getResult"
#
#
# First action is always "Calculator"
#
#
# Last action is always "getResult"
#

# @lc code=start
class Calculator:
    def __init__(self, value: float) -> None:
        """
        Interview explanation:
        JavaScript Calculator with method chaining; start with initial value.

        Algorithm:
        - Store result = value.

        Complexity: O(1).
        """
        self.result = float(value)

    def add(self, value: float) -> "Calculator":
        """
        Interview explanation:
        Add value to the running result.

        Algorithm:
        - result += value; return self.

        Complexity: O(1).
        """
        self.result += value
        return self

    def subtract(self, value: float) -> "Calculator":
        """
        Interview explanation:
        Subtract value from the running result.

        Algorithm:
        - result -= value; return self.

        Complexity: O(1).
        """
        self.result -= value
        return self

    def multiply(self, value: float) -> "Calculator":
        """
        Interview explanation:
        Multiply the running result by value.

        Algorithm:
        - result *= value; return self.

        Complexity: O(1).
        """
        self.result *= value
        return self

    def divide(self, value: float) -> "Calculator":
        """
        Interview explanation:
        Divide the running result by value; error on division by zero.

        Algorithm:
        - If value==0 raise; else result /= value; return self.

        Complexity: O(1).
        """
        if value == 0:
            raise ValueError("Division by zero is not allowed")
        self.result /= value
        return self

    def power(self, value: float) -> "Calculator":
        """
        Interview explanation:
        Raise the running result to power value.

        Algorithm:
        - result **= value; return self.

        Complexity: O(1).
        """
        self.result **= value
        return self

    def getResult(self) -> float:
        """
        Interview explanation:
        Return the current result.

        Algorithm:
        - Return stored result.

        Complexity: O(1).
        """
        return self.result


class Solution:
    def Calculator(self, value: float) -> Calculator:
        """
        Interview explanation:
        Factory for Calculator (mirrors JS constructor usage in harnesses).

        Algorithm:
        - Return Calculator(value).

        Complexity: O(1).
        """
        return Calculator(value)
# @lc code=end
