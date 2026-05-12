class Solution {
    public int equalSubstring(String s, String t, int maxCost) {
        int left = 0;
        int cost = 0;
        int best = 0;

        for (int right = 0; right < s.length(); right++) {
            cost += Math.abs(s.charAt(right) - t.charAt(right));

            while (cost > maxCost) {
                cost -= Math.abs(s.charAt(left) - t.charAt(left));
                left++;
            }

            best = Math.max(best, right - left + 1);
        }

        return best;
    }
}

/*
Explanation

Convert the two strings into an implicit cost array where cost[i] is the price
to change s[i] into t[i]. The task becomes finding the longest contiguous
subarray whose sum is at most maxCost.

Because all costs are nonnegative, a sliding window is the natural Java data
structure pattern: expand right, and while the current sum is too large, move
left. After the while loop, the window is valid and its length can update the
answer.

Edge cases: maxCost == 0 keeps only zero-cost runs; a one-character string is
handled naturally; if every character is too expensive, best remains 0.

Time complexity: O(n), since each pointer advances at most n times.
Space complexity: O(1).
*/
