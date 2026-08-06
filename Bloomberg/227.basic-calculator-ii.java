import java.util.*;

/**
 * Algorithm:
 * One pass with a stack. Defer addition/subtraction by pushing signed numbers;
 * immediately apply multiplication/division to the previous stack value because
 * they have higher precedence.
 *
 * Java data structures:
 * ArrayDeque<Integer> is used as the stack.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public int calculate(String s) {
        Deque<Integer> stack = new ArrayDeque<>();
        int num = 0;
        char op = '+';
        for (int i = 0; i <= s.length(); i++) {
            char ch = i == s.length() ? '+' : s.charAt(i);
            if (ch == ' ') {
                continue;
            }
            if (Character.isDigit(ch)) {
                num = num * 10 + ch - '0';
                continue;
            }
            if (op == '+') {
                stack.push(num);
            } else if (op == '-') {
                stack.push(-num);
            } else if (op == '*') {
                stack.push(stack.pop() * num);
            } else {
                stack.push(stack.pop() / num);
            }
            op = ch;
            num = 0;
        }
        int ans = 0;
        while (!stack.isEmpty()) {
            ans += stack.pop();
        }
        return ans;
    }
}

