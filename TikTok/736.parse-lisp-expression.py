#
# @lc app=leetcode id=736 lang=python3
#
# [736] Parse Lisp Expression
#
# https://leetcode.com/problems/parse-lisp-expression/description/
#
# algorithms
# Hard (53.85%)
# Likes:    506
# Dislikes: 370
# Total Accepted:    29.4K
# Total Submissions: 54.6K
# Testcase Example:  "\"(let x 2 (mult x (let x 3 y 4 (add x y))))\""
#
# You are given a string expression representing a Lisp-like expression to
# return the integer value of.
#
# The syntax for these expressions is given as follows.
#
# An expression is either an integer, let expression, add expression, mult
# expression, or an assigned variable. Expressions always evaluate to a single
# integer.
#
# (An integer could be positive or negative.)
#
# A let expression takes the form "(let v_1 e_1 v_2 e_2 ... v_n e_n expr)",
# where let is always the string "let", then there are one or more pairs of
# alternating variables and expressions, meaning that the first variable v_1 is
# assigned the value of the expression e_1, the second variable v_2 is assigned
# the value of the expression e_2, and so on sequentially; and then the value
# of this let expression is the value of the expression expr.
#
# An add expression takes the form "(add e_1 e_2)" where add is always the
# string "add", there are always two expressions e_1, e_2 and the result is the
# addition of the evaluation of e_1 and the evaluation of e_2.
#
# A mult expression takes the form "(mult e_1 e_2)" where mult is always the
# string "mult", there are always two expressions e_1, e_2 and the result is
# the multiplication of the evaluation of e1 and the evaluation of e2.
#
# For this question, we will use a smaller subset of variable names. A variable
# starts with a lowercase letter, then zero or more lowercase letters or
# digits. Additionally, for your convenience, the names "add", "let", and
# "mult" are protected and will never be used as variable names.
#
# Finally, there is the concept of scope. When an expression of a variable name
# is evaluated, within the context of that evaluation, the innermost scope (in
# terms of parentheses) is checked first for the value of that variable, and
# then outer scopes are checked sequentially. It is guaranteed that every
# expression is legal. Please see the examples for more details on the scope.
#
# Example 1:
#
# Input: expression = "(let x 2 (mult x (let x 3 y 4 (add x y))))"
# Output: 14
# Explanation: In the expression (add x y), when checking for the value of the
# variable x,
# we check from the innermost scope to the outermost in the context of the
# variable we are trying to evaluate.
# Since x = 3 is found first, the value of x is 3.
#
# Example 2:
#
# Input: expression = "(let x 3 x 2 x)"
# Output: 2
# Explanation: Assignment in let statements is processed sequentially.
#
# Example 3:
#
# Input: expression = "(let x 1 y 2 x (add x y) (add x y))"
# Output: 5
# Explanation: The first (add x y) evaluates as 3, and is assigned to x.
# The second (add x y) evaluates as 3+2 = 5.
#
# Constraints:
#
# 1 <= expression.length <= 2000
#
# There are no leading or trailing spaces in expression.
#
# All tokens are separated by a single space in expression.
#
# The answer and all intermediate calculations of that answer are guaranteed to
# fit in a 32-bit integer.
#
# The expression is guaranteed to be legal and evaluate to an integer.
#



# @lc code=start
class Solution:
    def evaluate(self, expression: str) -> int:
        """
        Interview explanation:
        Recursively parse a Lisp-like expression with let / add / mult and
        scoped variables. Tokenize on spaces and parentheses; evaluate with a
        stack of scopes so inner let bindings shadow outer ones.

        Algorithm:
        - Tokenize into '(', ')', identifiers, and integers.
        - evaluate_from(idx) consumes one expression:
          - atom: number or variable lookup through scopes (inner to outer)
          - (add x y) / (mult x y): evaluate both operands
          - (let v1 e1 ... vn en expr): push scope; bind sequentially; eval expr
        - Return the top-level value.

        Complexity: O(n) time and O(n) space for expression length n.
        """
        tokens = []
        i, n = 0, len(expression)
        while i < n:
            if expression[i] == " ":
                i += 1
                continue
            if expression[i] in "()":
                tokens.append(expression[i])
                i += 1
                continue
            j = i
            while j < n and expression[j] not in "() ":
                j += 1
            tokens.append(expression[i:j])
            i = j

        scopes = []

        def lookup(var: str) -> int:
            for scope in reversed(scopes):
                if var in scope:
                    return scope[var]
            raise KeyError(var)

        def evaluate_from(idx: int):
            if tokens[idx] != "(":
                t = tokens[idx]
                if t.lstrip("-").isdigit():
                    return int(t), idx + 1
                return lookup(t), idx + 1

            idx += 1
            op = tokens[idx]
            idx += 1
            if op == "add" or op == "mult":
                a, idx = evaluate_from(idx)
                b, idx = evaluate_from(idx)
                idx += 1  # ')'
                return (a + b if op == "add" else a * b), idx

            # let
            scopes.append({})
            while True:
                # Final expression when next token is '(' or the token after next is ')'
                if tokens[idx] == "(" or tokens[idx + 1] == ")":
                    val, idx = evaluate_from(idx)
                    idx += 1  # ')'
                    scopes.pop()
                    return val, idx
                var = tokens[idx]
                idx += 1
                val, idx = evaluate_from(idx)
                scopes[-1][var] = val

        val, _ = evaluate_from(0)
        return val
# @lc code=end


