import java.util.*;

/**
 * Algorithm:
 * Evaluate tokens with a stack. Numbers push; operators pop the right operand
 * then the left operand and push the result.
 *
 * Java data structures:
 * ArrayDeque<Integer> is used as a stack. Java integer division truncates
 * toward zero, matching the problem and the Python implementation's explicit
 * truncation.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public int evalRPN(String[] tokens) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (String token : tokens) {
            if (!isOperator(token)) {
                stack.push(Integer.parseInt(token));
                continue;
            }
            int b = stack.pop();
            int a = stack.pop();
            if (token.equals("+")) {
                stack.push(a + b);
            } else if (token.equals("-")) {
                stack.push(a - b);
            } else if (token.equals("*")) {
                stack.push(a * b);
            } else {
                stack.push(a / b);
            }
        }
        return stack.peek();
    }

    private boolean isOperator(String token) {
        return token.length() == 1 && "+-*/".contains(token);
    }
}

