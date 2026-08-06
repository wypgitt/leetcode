import java.util.*;

/**
 * Algorithm:
 * Store each pushed value together with the minimum value at that stack depth.
 * Then getMin is just the second field of the top entry.
 *
 * Java data structures:
 * ArrayDeque<int[]> acts as a stack of {value, currentMin}.
 *
 * Complexity:
 * All operations are O(1), space O(n).
 */
class MinStack {
    private final Deque<int[]> stack;

    public MinStack() {
        stack = new ArrayDeque<>();
    }

    public void push(int val) {
        int currentMin = stack.isEmpty() ? val : Math.min(val, stack.peek()[1]);
        stack.push(new int[] {val, currentMin});
    }

    public void pop() {
        stack.pop();
    }

    public int top() {
        return stack.peek()[0];
    }

    public int getMin() {
        return stack.peek()[1];
    }
}

