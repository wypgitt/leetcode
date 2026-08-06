import java.util.*;

/**
 * Algorithm:
 * Sliding window with a map from character to most recent index. When a repeat
 * appears inside the current window, move the left boundary just past the old
 * occurrence.
 *
 * Java data structures:
 * HashMap<Character, Integer> handles general Java char input. For ASCII-only
 * input, an int[128] could be faster.
 *
 * Complexity:
 * Time O(n), space O(min(n, alphabet)).
 */
class Solution {
    public int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> lastSeen = new HashMap<>();
        int left = 0;
        int best = 0;
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            Integer old = lastSeen.get(ch);
            if (old != null && old >= left) {
                left = old + 1;
            }
            lastSeen.put(ch, right);
            best = Math.max(best, right - left + 1);
        }
        return best;
    }
}

