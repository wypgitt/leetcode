/*
 * @lc app=leetcode id=527 lang=java
 *
 * [527] Word Abbreviation
 *
 * Maintain one prefix length per word. Recompute abbreviations, group equal
 * abbreviations, and increase prefix length only for conflicting groups until
 * every abbreviation is unique or no shorter than the original.
 *
 * Java note: HashMap<String,List<Integer>> is used for conflict grouping.
 *
 * Time: O(rounds * n * word length). Space: O(n).
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    public List<String> wordsAbbreviation(List<String> words) {
        int n = words.size();
        int[] prefixLengths = new int[n];
        for (int i = 0; i < n; i++) {
            prefixLengths[i] = 1;
        }

        while (true) {
            Map<String, List<Integer>> groups = new HashMap<>();
            for (int i = 0; i < n; i++) {
                groups.computeIfAbsent(abbreviate(words.get(i), prefixLengths[i]), unused -> new ArrayList<>()).add(i);
            }

            boolean hasConflict = false;
            for (List<Integer> indices : groups.values()) {
                if (indices.size() <= 1) {
                    continue;
                }
                hasConflict = true;
                for (int index : indices) {
                    prefixLengths[index]++;
                }
            }
            if (!hasConflict) {
                break;
            }
        }

        List<String> answer = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            answer.add(abbreviate(words.get(i), prefixLengths[i]));
        }
        return answer;
    }

    private String abbreviate(String word, int prefixLength) {
        int omitted = word.length() - prefixLength - 1;
        String abbreviation = word.substring(0, prefixLength) + omitted + word.charAt(word.length() - 1);
        return abbreviation.length() < word.length() ? abbreviation : word;
    }
}
// @lc code=end
