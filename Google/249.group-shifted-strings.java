import java.util.*;

/**
 * Algorithm:
 * Normalize each string by recording each character's offset from the first
 * character modulo 26. Shifted strings share the same normalized key.
 *
 * Java data structures:
 * HashMap<String, List<String>> groups by delimiter-separated offset key.
 *
 * Complexity:
 * Time O(total characters), space O(total characters).
 */
class Solution {
    public List<List<String>> groupStrings(String[] strings) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String s : strings) {
            int base = s.charAt(0) - 'a';
            StringBuilder key = new StringBuilder();
            for (int i = 0; i < s.length(); i++) {
                int offset = (s.charAt(i) - 'a' - base + 26) % 26;
                key.append('#').append(offset);
            }
            groups.computeIfAbsent(key.toString(), k -> new ArrayList<>()).add(s);
        }
        return new ArrayList<>(groups.values());
    }
}

