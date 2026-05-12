import java.util.*;

class Solution {
    public int mctFromLeafValues(int[] arr) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(Integer.MAX_VALUE);
        int cost = 0;

        for (int value : arr) {
            while (stack.peek() <= value) {
                int middle = stack.pop();
                cost += middle * Math.min(stack.peek(), value);
            }
            stack.push(value);
        }

        while (stack.size() > 2) {
            cost += stack.pop() * stack.peek();
        }

        return cost;
    }
}

