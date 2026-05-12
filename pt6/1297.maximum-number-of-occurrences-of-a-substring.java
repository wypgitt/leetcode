import java.util.HashMap;
import java.util.Map;

class Solution {
    public int maxFreq(String s, int maxLetters, int minSize, int maxSize) {
        Map<Character, Integer> window = new HashMap<>();
        Map<String, Integer> freq = new HashMap<>();
        int distinct = 0;
        int best = 0;

        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            if (window.getOrDefault(ch, 0) == 0) {
                distinct++;
            }
            window.put(ch, window.getOrDefault(ch, 0) + 1);

            if (right >= minSize) {
                char leftCh = s.charAt(right - minSize);
                window.put(leftCh, window.get(leftCh) - 1);
                if (window.get(leftCh) == 0) {
                    distinct--;
                }
            }

            if (right >= minSize - 1 && distinct <= maxLetters) {
                String sub = s.substring(right - minSize + 1, right + 1);
                int count = freq.getOrDefault(sub, 0) + 1;
                freq.put(sub, count);
                best = Math.max(best, count);
            }
        }

        return best;
    }
}

/*
Explanation

It is enough to count substrings of length minSize. Any longer valid substring
has a minSize prefix that appears at least as often, so the maximum frequency
can always be achieved by some minSize substring.

Use a fixed-size sliding window with a character-frequency HashMap to maintain
the number of distinct letters. When the window is valid, count that substring
in another HashMap.

maxSize is intentionally unused because of the prefix argument above.

Edge cases: maxLetters == 1; overlapping repeated substrings; no valid window
returns 0.

Time complexity: O(n * minSize), due to substring creation/hash work.
Space complexity: O(n * minSize) for substring keys in the worst case.
*/
