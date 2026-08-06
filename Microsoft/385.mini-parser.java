import java.util.*;

/**
 * Algorithm:
 * Parse the serialized nested list with a stack of open NestedInteger lists.
 * A '[' creates a new list. A comma or ']' ends a pending numeric slice. A ']'
 * also closes the current list and attaches it to its parent.
 *
 * Java data structures:
 * ArrayDeque is used as a stack. It is preferred over the legacy Stack class
 * because it has less synchronization overhead and clearer deque operations.
 *
 * Complexity:
 * Time O(n), where n is the string length. Auxiliary space O(depth), excluding
 * the returned NestedInteger tree.
 */
class Solution {
    public NestedInteger deserialize(String s) {
        if (s.charAt(0) != '[') {
            return new NestedInteger(Integer.parseInt(s));
        }

        Deque<NestedInteger> stack = new ArrayDeque<>();
        int numberStart = -1;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '[') {
                stack.push(new NestedInteger());
            } else if (ch == ']') {
                if (numberStart != -1) {
                    stack.peek().add(new NestedInteger(Integer.parseInt(s.substring(numberStart, i))));
                    numberStart = -1;
                }
                NestedInteger finished = stack.pop();
                if (stack.isEmpty()) {
                    return finished;
                }
                stack.peek().add(finished);
            } else if (ch == ',') {
                if (numberStart != -1) {
                    stack.peek().add(new NestedInteger(Integer.parseInt(s.substring(numberStart, i))));
                    numberStart = -1;
                }
            } else if (numberStart == -1) {
                numberStart = i;
            }
        }
        return new NestedInteger();
    }
}

