import java.util.*;

/**
 * Algorithm:
 * Ternary expressions are right-associative, so scan from right to left. When
 * a condition is followed by a pending '?', the true and false branches on the
 * stack have already been reduced to one character each.
 *
 * Java data structures:
 * ArrayDeque<Character> is used as a stack.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public String parseTernary(String expression) {
        Deque<Character> stack = new ArrayDeque<>();
        for (int i = expression.length() - 1; i >= 0; i--) {
            char ch = expression.charAt(i);
            if (!stack.isEmpty() && stack.peek() == '?') {
                stack.pop();
                char trueExpr = stack.pop();
                stack.pop();
                char falseExpr = stack.pop();
                stack.push(ch == 'T' ? trueExpr : falseExpr);
            } else {
                stack.push(ch);
            }
        }
        return String.valueOf(stack.peek());
    }
}

