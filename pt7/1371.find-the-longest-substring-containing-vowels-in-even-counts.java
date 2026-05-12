import java.util.HashMap;
import java.util.Map;

/*
 * LeetCode 1371 - Find the Longest Substring Containing Vowels in Even Counts
 */
class Solution {
    public int findTheLongestSubstring(String s) {
        Map<Integer, Integer> firstSeen = new HashMap<>();
        firstSeen.put(0, -1);

        int mask = 0;
        int best = 0;

        for (int i = 0; i < s.length(); i++) {
            int bit = vowelBit(s.charAt(i));
            if (bit != -1) {
                mask ^= 1 << bit;
            }

            if (firstSeen.containsKey(mask)) {
                best = Math.max(best, i - firstSeen.get(mask));
            } else {
                firstSeen.put(mask, i);
            }
        }

        return best;
    }

    private int vowelBit(char c) {
        if (c == 'a') return 0;
        if (c == 'e') return 1;
        if (c == 'i') return 2;
        if (c == 'o') return 3;
        if (c == 'u') return 4;
        return -1;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * We only need parity, not exact counts. Encode whether each vowel count is odd
 * in a 5-bit mask. If the same mask appears at two indices, the substring
 * between them has even counts for all vowels.
 *
 * Java data structures:
 * `HashMap<Integer, Integer>` stores the earliest index for each mask. There
 * are at most 32 masks, so this is constant-size in practice.
 *
 * Edge cases:
 * - No vowels means mask stays 0 and the whole string is valid.
 * - The initial mask 0 at index -1 allows substrings starting at index 0.
 * - Consonants do not affect the mask.
 *
 * Complexity:
 * Time O(n).
 * Space O(1), at most 32 masks.
 */
