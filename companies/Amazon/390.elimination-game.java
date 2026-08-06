/**
 * Algorithm:
 * The remaining numbers always form an arithmetic sequence. Track only the
 * first number, the gap, the count left, and the deletion direction. The first
 * number advances on every left-to-right round and on right-to-left rounds with
 * an odd count.
 *
 * Complexity:
 * Time O(log n) because the count halves each round. Space O(1).
 */
class Solution {
    public int lastRemaining(int n) {
        int head = 1;
        int step = 1;
        int remaining = n;
        boolean leftToRight = true;

        while (remaining > 1) {
            if (leftToRight || remaining % 2 == 1) {
                head += step;
            }
            remaining /= 2;
            step *= 2;
            leftToRight = !leftToRight;
        }
        return head;
    }
}

