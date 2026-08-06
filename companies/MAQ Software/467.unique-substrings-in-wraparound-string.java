/**
 * Algorithm:
 * Track the current consecutive run in the infinite wraparound alphabet. For
 * each ending character, only the maximum run length matters because it
 * represents all unique substrings ending at that character.
 *
 * Java data structures:
 * A fixed int[26] stores the best run length by ending character.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int findSubstringInWraproundString(String s) {
        int[] best = new int[26];
        int run = 0;
        char prev = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (prev != 0 && (ch - prev + 26) % 26 == 1) {
                run++;
            } else {
                run = 1;
            }
            int idx = ch - 'a';
            best[idx] = Math.max(best[idx], run);
            prev = ch;
        }
        int ans = 0;
        for (int x : best) {
            ans += x;
        }
        return ans;
    }
}

