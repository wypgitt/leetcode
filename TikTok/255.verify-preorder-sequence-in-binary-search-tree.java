import java.util.*;

/**
 * Algorithm:
 * Simulate preorder traversal bounds with a stack. Values popped from the stack
 * become lower bounds for the current right subtree; any later value below that
 * lower bound is invalid.
 *
 * Java data structures:
 * ArrayDeque<Integer> is the stack of ancestor values.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public boolean verifyPreorder(int[] preorder) {
        Deque<Integer> stack = new ArrayDeque<>();
        int lower = Integer.MIN_VALUE;
        for (int value : preorder) {
            if (value < lower) {
                return false;
            }
            while (!stack.isEmpty() && value > stack.peek()) {
                lower = stack.pop();
            }
            stack.push(value);
        }
        return true;
    }
}

