import java.util.*;

/**
 * Algorithm:
 * Anagrams share the same lowercase character counts. Use a 26-count signature
 * as the grouping key.
 *
 * Java data structures:
 * HashMap<String, List<String>> groups words. The key is a delimiter-separated
 * count string, which is safe from ambiguity.
 *
 * Complexity:
 * Time O(total characters), space O(number of strings * 26) plus output.
 */
class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String word : strs) {
            int[] counts = new int[26];
            for (int i = 0; i < word.length(); i++) {
                counts[word.charAt(i) - 'a']++;
            }
            StringBuilder keyBuilder = new StringBuilder();
            for (int count : counts) {
                keyBuilder.append('#').append(count);
            }
            String key = keyBuilder.toString();
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(word);
        }
        return new ArrayList<>(groups.values());
    }
}

