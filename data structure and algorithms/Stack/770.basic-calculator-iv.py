#
# @lc app=leetcode id=770 lang=python3
#
# [770] Basic Calculator IV
#
# https://leetcode.com/problems/basic-calculator-iv/description/
#
# algorithms
# Hard (49.86%)
# Likes:    182
# Dislikes: 1447
# Total Accepted:    17.2K
# Total Submissions: 34.6K
# Testcase Example:  "\"e + 8 - a + 5\""
#
# Given an expression such as expression = "e + 8 - a + 5" and an evaluation
# map such as {"e": 1} (given in terms of evalvars = ["e"] and evalints = [1]),
# return a list of tokens representing the simplified expression, such as
# ["-1*a","14"]
#
# An expression alternates chunks and symbols, with a space separating each
# chunk and symbol.
#
# A chunk is either an expression in parentheses, a variable, or a non-negative
# integer.
#
# A variable is a string of lowercase letters (not including digits.) Note that
# variables can be multiple letters, and note that variables never have a
# leading coefficient or unary operator like "2x" or "-x".
#
# Expressions are evaluated in the usual order: brackets first, then
# multiplication, then addition and subtraction.
#
# For example, expression = "1 + 2 * 3" has an answer of ["7"].
#
# The format of the output is as follows:
#
# For each term of free variables with a non-zero coefficient, we write the
# free variables within a term in sorted order lexicographically.
#
# For example, we would never write a term like "b*a*c", only "a*b*c".
#
# Terms have degrees equal to the number of free variables being multiplied,
# counting multiplicity. We write the largest degree terms of our answer first,
# breaking ties by lexicographic order ignoring the leading coefficient of the
# term.
#
# For example, "a*a*b*c" has degree 4.
#
# The leading coefficient of the term is placed directly to the left with an
# asterisk separating it from the variables (if they exist.) A leading
# coefficient of 1 is still printed.
#
# An example of a well-formatted answer is ["-2*a*a*a", "3*a*a*b", "3*b*b",
# "4*a", "5*c", "-6"].
#
# Terms (including constant terms) with coefficient 0 are not included.
#
# For example, an expression of "0" has an output of [].
#
# Note: You may assume that the given expression is always valid. All
# intermediate results will be in the range of [-2^31, 2^31 - 1].
#
# Example 1:
#
# Input: expression = "e + 8 - a + 5", evalvars = ["e"], evalints = [1]
# Output: ["-1*a","14"]
#
# Example 2:
#
# Input: expression = "e - 8 + temperature - pressure", evalvars = ["e",
# "temperature"], evalints = [1, 12]
# Output: ["-1*pressure","5"]
#
# Example 3:
#
# Input: expression = "(e + 8) * (e - 8)", evalvars = [], evalints = []
# Output: ["1*e*e","-64"]
#
# Constraints:
#
# 1 <= expression.length <= 250
#
# expression consists of lowercase English letters, digits, '+', '-', '*', '(',
# ')', ' '.
#
# expression does not contain any leading or trailing spaces.
#
# All the tokens in expression are separated by a single space.
#
# 0 <= evalvars.length <= 100
#
# 1 <= evalvars[i].length <= 20
#
# evalvars[i] consists of lowercase English letters.
#
# evalints.length == evalvars.length
#
# -100 <= evalints[i] <= 100
#


# @lc code=start
from collections import Counter
from typing import Dict, List, Tuple


class Solution:
    def basicCalculatorIV(
        self, expression: str, evalvars: List[str], evalints: List[int]
    ) -> List[str]:
        """
        Interview explanation:
        Evaluate an expression with +, -, *, parentheses, integers, and free
        variables into a polynomial. Substitute known variables first. Represent
        each polynomial as Counter mapping sorted variable-tuple -> coefficient;
        combine via add/sub/mul. Format terms by degree desc, then lex order.

        Algorithm:
        - known = dict(zip(evalvars, evalints))
        - Tokenize; shunting-yard / recursive descent for + - * and ()
        - Poly ops on Counter[Tuple[str,...], int]
        - Emit [coeff][*var...] for nonzero coeffs, sorted

        Complexity: O(T * P log P) roughly for expression size and poly terms.
        """
        known: Dict[str, int] = dict(zip(evalvars, evalints))

        def make(coeff: int = 0, vars_: Tuple[str, ...] = ()) -> Counter:
            c: Counter = Counter()
            if coeff:
                c[vars_] = coeff
            return c

        def add(a: Counter, b: Counter) -> Counter:
            res = a.copy()
            for k, v in b.items():
                res[k] += v
                if res[k] == 0:
                    del res[k]
            return res

        def sub(a: Counter, b: Counter) -> Counter:
            return add(a, Counter({k: -v for k, v in b.items()}))

        def mul(a: Counter, b: Counter) -> Counter:
            res: Counter = Counter()
            for ka, va in a.items():
                for kb, vb in b.items():
                    key = tuple(sorted(ka + kb))
                    res[key] += va * vb
                    if res[key] == 0:
                        del res[key]
            return res

        # tokenize
        tokens: List[str] = []
        i, n = 0, len(expression)
        while i < n:
            if expression[i] == " ":
                i += 1
            elif expression[i] in "+-*()":
                tokens.append(expression[i])
                i += 1
            else:
                j = i
                while j < n and expression[j] not in "+-*() ":
                    j += 1
                tokens.append(expression[i:j])
                i = j

        prec = {"+": 1, "-": 1, "*": 2}

        def atom(tok: str) -> Counter:
            if tok.lstrip("-").isdigit():
                return make(int(tok))
            if tok in known:
                return make(known[tok])
            return make(1, (tok,))

        # shunting yard to RPN then eval
        output: List = []
        ops: List[str] = []
        for tok in tokens:
            if tok not in "+-*()":
                output.append(atom(tok))
            elif tok in prec:
                while (
                    ops
                    and ops[-1] in prec
                    and prec[ops[-1]] >= prec[tok]
                ):
                    output.append(ops.pop())
                ops.append(tok)
            elif tok == "(":
                ops.append(tok)
            elif tok == ")":
                while ops and ops[-1] != "(":
                    output.append(ops.pop())
                ops.pop()
        while ops:
            output.append(ops.pop())

        stack: List[Counter] = []
        for item in output:
            if isinstance(item, str):
                b = stack.pop()
                a = stack.pop()
                if item == "+":
                    stack.append(add(a, b))
                elif item == "-":
                    stack.append(sub(a, b))
                else:
                    stack.append(mul(a, b))
            else:
                stack.append(item)

        poly = stack[0] if stack else Counter()

        def term_key(vars_coeff):
            vars_, coeff = vars_coeff
            return (-len(vars_), vars_)

        ans = []
        for vars_, coeff in sorted(poly.items(), key=term_key):
            if coeff == 0:
                continue
            if not vars_:
                ans.append(str(coeff))
            else:
                ans.append(str(coeff) + "*" + "*".join(vars_))
        return ans
# @lc code=end

