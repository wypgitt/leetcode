import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Queue;

class Solution {
    public List<Integer> countSteppingNumbers(int low, int high) {
        List<Integer> ans = new ArrayList<>();
        Queue<Long> queue = new ArrayDeque<>();

        for (long digit = 0; digit <= 9; digit++) {
            queue.offer(digit);
        }

        while (!queue.isEmpty()) {
            long num = queue.poll();
            if (num > high) {
                continue;
            }
            if (num >= low) {
                ans.add((int) num);
            }
            if (num == 0) {
                continue;
            }

            long last = num % 10;
            if (last > 0) {
                queue.offer(num * 10 + last - 1);
            }
            if (last < 9) {
                queue.offer(num * 10 + last + 1);
            }
        }

        Collections.sort(ans);
        return ans;
    }
}

/*
Explanation

A stepping number is built by appending lastDigit - 1 or lastDigit + 1. BFS
starts from digits 0 through 9 and generates only valid stepping-number
prefixes.

The queue is the right structure because every queued value is a valid prefix
that may produce larger valid numbers. We use long during generation to avoid
temporary overflow before comparing to high.

Zero is valid if it is in range, but it is not extended because leading-zero
numbers such as 01 are not valid.

Edge cases: ranges containing 0; high below 10; last digit 0 or 9 has only one
extension. Sorting gives increasing answer order.

Time complexity: O(k log k), where k is the number of generated answers.
Space complexity: O(k).
*/
