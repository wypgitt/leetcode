#
# @lc app=leetcode id=1106 lang=python3
#
# [1106] Parsing A Boolean Expression
#

# --- Interview notes (grammar, stack evaluation, operator semantics, complexity, edges, tests) ---
#
# Grammar (given)
# • 't' → true, 'f' → false.
# • !(expr) → logical NOT of one subexpression.
# • &(e1,e2,…) → AND of one or more subexpressions (comma-separated inside parentheses).
# • |(e1,e2,…) → OR of one or more subexpressions.
#
# Why a stack (iterative evaluation)
# Parentheses nest arbitrarily; each closing ')' finishes one compound expression and collapses it to a single
# truth value ('t' or 'f') that acts like an atom for outer operators. A stack naturally holds pending operators
# and already-evaluated Boolean atoms from left to right.
#
# Scan rule (editorial pattern)
# Iterate characters left to right:
# • Push 't', 'f', '!', '&', '|' onto the stack.
# • Ignore '(' and ',' — they only structure grouping/separation and never need to be stored.
# • On ')':
#     1. Pop all consecutive 't'/'f' values immediately below the top — these are the evaluated arguments of the
#        group just closed. Count how many true (t_cnt) and false (f_cnt) among them.
#     2. Pop the operator ('!', '&', or '|') that sits under those operands (it was pushed when its keyword was
#        seen).
#     3. Combine operands according to the operator and push one resulting character back:
#           !  : exactly one operand; NOT(false)=true, NOT(true)=false  →  't' if operand was 'f' else 'f'.
#           &  : AND is false iff any argument is false  →  'f' if any false (f_cnt>0) else 't'.
#           |  : OR is true iff any argument is true    →  't' if any true (t_cnt>0) else 'f'.
#
# End state
# After the whole string, exactly one symbol remains on the stack — 't' or 'f'. Compare to 't' for the Python bool.
#
# Correctness intuition
# Postfix-style collapse on each ')' matches recursively evaluating innermost parentheses first; skipping '('
# and ',' preserves order because operands were pushed as their subexpressions completed earlier.
#
# Time complexity
# O(n) — each character pushed/popped a constant number of times.
#
# Space complexity
# O(n) stack depth in worst case (nested operators).
#
# Edge cases
# • !(t), &(t), |(f) — unary-style groups with one argument; counting logic still matches.
# • Deep nesting — stack depth proportional to nesting depth.
#
# Tests (statement)
# "&(|(f))" → false ; "|(f,f,f,t)" → true ; "!(&(f,t))" → true.
#
# Improvements / alternatives
# • Recursive descent with index pointer — same O(n) time, O(recursion depth) space; stack avoids recursion limit.
#
# --- end notes ---

# @lc code=start
class Solution:
    def parseBoolExpr(self, expression: str) -> bool:
        stk: list[str] = []
        for c in expression:
            if c in "tf!&|":
                stk.append(c)
            elif c == ")":
                t_cnt = f_cnt = 0
                while stk[-1] in "tf":
                    t_cnt += stk[-1] == "t"
                    f_cnt += stk[-1] == "f"
                    stk.pop()
                op = stk.pop()
                if op == "!":
                    res = "t" if f_cnt else "f"
                elif op == "&":
                    res = "f" if f_cnt else "t"
                else:
                    res = "t" if t_cnt else "f"
                stk.append(res)
        return stk[0] == "t"


# @lc code=end
