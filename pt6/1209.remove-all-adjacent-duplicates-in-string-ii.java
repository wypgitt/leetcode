import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public String removeDuplicates(String s, int k) {
        Deque<int[]> stack = new ArrayDeque<>();

        for (char ch : s.toCharArray()) {
            if (!stack.isEmpty() && stack.peekLast()[0] == ch) {
                stack.peekLast()[1]++;
            } else {
                stack.addLast(new int[] {ch, 1});
            }

            if (stack.peekLast()[1] == k) {
                stack.removeLast();
            }
        }

        StringBuilder ans = new StringBuilder();
        for (int[] run : stack) {
            for (int i = 0; i < run[1]; i++) {
                ans.append((char) run[0]);
            }
        }
        return ans.toString();
    }
}

/*
Explanation

Use a stack of compressed runs: [character, count]. The next character either
extends the most recent run or starts a new run. When the count reaches k, pop
that run immediately.

The stack is ideal because deletions only affect the newest surviving run. If a
run is removed, the previous stack entry is automatically exposed and can merge
with future characters.

Java choices: ArrayDeque is the standard stack/deque implementation; a
StringBuilder avoids repeated string concatenation when reconstructing.

Edge cases: k == 1 removes all characters; alternating characters never form a
large run; chained deletions are handled by popping.

Time complexity: O(n).
Space complexity: O(n).
*/
