import java.util.*;

/**
 * Algorithm:
 * Sliding window with a character count map. Expand right, and while more than
 * two distinct characters are present, shrink from the left.
 *
 * Java data structures:
 * HashMap<Character, Integer> stores counts in the current window.
 *
 * Complexity:
 * Time O(n), space O(1) because at most three character keys exist before
 * shrinking.
 */
class Solution {
    public int lengthOfLongestSubstringTwoDistinct(String s) {
        Map<Character, Integer> counts = new HashMap<>();
        int left = 0;
        int best = 0;
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            counts.put(ch, counts.getOrDefault(ch, 0) + 1);
            while (counts.size() > 2) {
                char old = s.charAt(left++);
                int next = counts.get(old) - 1;
                if (next == 0) {
                    counts.remove(old);
                } else {
                    counts.put(old, next);
                }
            }
            best = Math.max(best, right - left + 1);
        }
        return best;
    }
}

