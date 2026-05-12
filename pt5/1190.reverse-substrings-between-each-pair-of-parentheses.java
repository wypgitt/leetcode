import java.util.*;

class Solution {
    public String reverseParentheses(String s) {
        StringBuilder stack = new StringBuilder();

        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch != ')') {
                stack.append(ch);
                continue;
            }

            StringBuilder reversed = new StringBuilder();
            while (stack.charAt(stack.length() - 1) != '(') {
                reversed.append(stack.charAt(stack.length() - 1));
                stack.deleteCharAt(stack.length() - 1);
            }
            stack.deleteCharAt(stack.length() - 1);
            stack.append(reversed);
        }

        return stack.toString();
    }
}

