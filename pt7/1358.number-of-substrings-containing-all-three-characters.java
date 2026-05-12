import java.util.Arrays;

/*
 * LeetCode 1358 - Number of Substrings Containing All Three Characters
 */
class Solution {
    public int numberOfSubstrings(String s) {
        int[] lastSeen = {-1, -1, -1};
        int total = 0;

        for (int right = 0; right < s.length(); right++) {
            lastSeen[s.charAt(right) - 'a'] = right;
            total += Arrays.stream(lastSeen).min().getAsInt() + 1;
        }

        return total;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * For each ending index, count how many starting positions produce a substring
 * containing a, b, and c. If the latest positions of all three letters are
 * known, every start from 0 through the minimum latest position is valid.
 *
 * Java data structures:
 * `int[3] lastSeen` stores latest index for a, b, c. This is a tiny fixed-size
 * state, so no map is needed.
 *
 * Edge cases:
 * - Before all three characters appear, the minimum is -1 and contributes 0.
 * - Repeated characters only update their latest index.
 * - The answer can be accumulated in int under the constraints.
 *
 * Complexity:
 * Time O(n).
 * Space O(1).
 */
