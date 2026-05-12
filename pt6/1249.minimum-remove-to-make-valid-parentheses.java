import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashSet;
import java.util.Set;

class Solution {
    public String minRemoveToMakeValid(String s) {
        Deque<Integer> stack = new ArrayDeque<>();
        Set<Integer> remove = new HashSet<>();

        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '(') {
                stack.push(i);
            } else if (ch == ')') {
                if (stack.isEmpty()) {
                    remove.add(i);
                } else {
                    stack.pop();
                }
            }
        }

        remove.addAll(stack);
        StringBuilder ans = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if (!remove.contains(i)) {
                ans.append(s.charAt(i));
            }
        }
        return ans.toString();
    }
}

/*
Explanation

Use a stack of indices for unmatched opening parentheses. A closing parenthesis
matches the latest opening parenthesis if possible; otherwise it must be
removed. After the scan, any opening indices still in the stack are unmatched
and must also be removed.

The stack is the right data structure because parentheses match in last-opened,
first-closed order.

Edge cases: extra ')' at the front; extra '(' at the end; letters are
preserved.

Time complexity: O(n).
Space complexity: O(n).
*/
