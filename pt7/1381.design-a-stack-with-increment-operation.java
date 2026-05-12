import java.util.ArrayList;
import java.util.List;

/*
 * LeetCode 1381 - Design a Stack With Increment Operation
 */
class CustomStack {
    private final int maxSize;
    private final List<Integer> stack;
    private final List<Integer> pendingIncrement;

    public CustomStack(int maxSize) {
        this.maxSize = maxSize;
        this.stack = new ArrayList<>();
        this.pendingIncrement = new ArrayList<>();
    }

    public void push(int x) {
        if (stack.size() == maxSize) {
            return;
        }
        stack.add(x);
        pendingIncrement.add(0);
    }

    public int pop() {
        if (stack.isEmpty()) {
            return -1;
        }

        int index = stack.size() - 1;
        int extra = pendingIncrement.get(index);
        if (index > 0) {
            pendingIncrement.set(index - 1, pendingIncrement.get(index - 1) + extra);
        }

        pendingIncrement.remove(index);
        return stack.remove(index) + extra;
    }

    public void increment(int k, int val) {
        if (stack.isEmpty()) {
            return;
        }

        int index = Math.min(k, stack.size()) - 1;
        pendingIncrement.set(index, pendingIncrement.get(index) + val);
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * A direct increment of the bottom k elements is O(k). Instead, use lazy
 * propagation: store an increment marker at the highest affected index. When
 * popping, pass that marker down one level so it eventually applies to all
 * lower elements.
 *
 * Java data structures:
 * `ArrayList<Integer> stack` stores actual pushed values.
 * `ArrayList<Integer> pendingIncrement` mirrors stack indices and stores lazy
 * increments for prefixes.
 *
 * Edge cases:
 * - push on a full stack does nothing.
 * - pop on an empty stack returns -1.
 * - increment with k larger than size affects all current elements.
 *
 * Complexity:
 * push O(1), pop O(1), increment O(1) amortized for ArrayList end operations.
 * Space O(maxSize).
 */
