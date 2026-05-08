// Translated from 1106.parsing-a-boolean-expression.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1106 lang=python3
// #
// # [1106] Parsing A Boolean Expression
// #
// 
// # --- Interview notes (grammar, stack evaluation, operator semantics, complexity, edges, tests) ---
// #
// # Grammar (given)
// # • 't' → true, 'f' → false.
// # • !(expr) → logical NOT of one subexpression.
// # • &(e1,e2,…) → AND of one or more subexpressions (comma-separated inside parentheses).
// # • |(e1,e2,…) → OR of one or more subexpressions.
// #
// # Why a stack (iterative evaluation)
// # Parentheses nest arbitrarily; each closing ')' finishes one compound expression and collapses it to a single
// # truth value ('t' or 'f') that acts like an atom for outer operators. A stack naturally holds pending operators
// # and already-evaluated Boolean atoms from left to right.
// #
// # Scan rule (editorial pattern)
// # Iterate characters left to right:
// # • Push 't', 'f', '!', '&', '|' onto the stack.
// # • Ignore '(' and ',' — they only structure grouping/separation and never need to be stored.
// # • On ')':
// #     1. Pop all consecutive 't'/'f' values immediately below the top — these are the evaluated arguments of the
// #        group just closed. Count how many true (t_cnt) and false (f_cnt) among them.
// #     2. Pop the operator ('!', '&', or '|') that sits under those operands (it was pushed when its keyword was
// #        seen).
// #     3. Combine operands according to the operator and push one resulting character back:
// #           !  : exactly one operand; NOT(false)=true, NOT(true)=false  →  't' if operand was 'f' else 'f'.
// #           &  : AND is false iff any argument is false  →  'f' if any false (f_cnt>0) else 't'.
// #           |  : OR is true iff any argument is true    →  't' if any true (t_cnt>0) else 'f'.
// #
// # End state
// # After the whole string, exactly one symbol remains on the stack — 't' or 'f'. Compare to 't' for the Python bool.
// #
// # Correctness intuition
// # Postfix-style collapse on each ')' matches recursively evaluating innermost parentheses first; skipping '('
// # and ',' preserves order because operands were pushed as their subexpressions completed earlier.
// #
// # Time complexity
// # O(n) — each character pushed/popped a constant number of times.
// #
// # Space complexity
// # O(n) stack depth in worst case (nested operators).
// #
// # Edge cases
// # • !(t), &(t), |(f) — unary-style groups with one argument; counting logic still matches.
// # • Deep nesting — stack depth proportional to nesting depth.
// #
// # Tests (statement)
// # "&(|(f))" → false ; "|(f,f,f,t)" → true ; "!(&(f,t))" → true.
// #
// # Improvements / alternatives
// # • Recursive descent with index pointer — same O(n) time, O(recursion depth) space; stack avoids recursion limit.
// #
// # --- end notes ---
// 
// # @lc code=start
// class Solution:
//     def parseBoolExpr(self, expression: str) -> bool:
//         stk: list[str] = []
//         for c in expression:
//             if c in "tf!&|":
//                 stk.append(c)
//             elif c == ")":
//                 t_cnt = f_cnt = 0
//                 while stk[-1] in "tf":
//                     t_cnt += stk[-1] == "t"
//                     f_cnt += stk[-1] == "f"
//                     stk.pop()
//                 op = stk.pop()
//                 if op == "!":
//                     res = "t" if f_cnt else "f"
//                 elif op == "&":
//                     res = "f" if f_cnt else "t"
//                 else:
//                     res = "t" if t_cnt else "f"
//                 stk.append(res)
//         return stk[0] == "t"
// 
// 
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
public:
    bool parseBoolExpr(string expression) {
        vector<char> st;
        for (char c : expression) {
            if (c == 't' || c == 'f' || c == '!' || c == '&' || c == '|') st.push_back(c);
            else if (c == ')') {
                int tc = 0, fc = 0;
                while (!st.empty() && (st.back() == 't' || st.back() == 'f')) {
                    tc += st.back() == 't';
                    fc += st.back() == 'f';
                    st.pop_back();
                }
                char op = st.back();
                st.pop_back();
                char res;
                if (op == '!') res = fc ? 't' : 'f';
                else if (op == '&') res = fc ? 'f' : 't';
                else res = tc ? 't' : 'f';
                st.push_back(res);
            }
        }
        return st[0] == 't';
    }
};
