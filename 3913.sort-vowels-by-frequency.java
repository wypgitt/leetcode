/*
 * @lc app=leetcode id=3913 lang=java
 *
 * [3913] Sort Vowels by Frequency
 *
 * Count lowercase vowels and remember their first position. Sort present vowels
 * by descending frequency, then first occurrence, and refill the original vowel
 * slots from that stream.
 *
 * Time: O(n + V log V). Space: O(n), V <= 5.
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public String sortVowels(String s) {
        int[] count = new int[26];
        int[] first = new int[26];
        for (int i = 0; i < 26; i++) {
            first[i] = -1;
        }

        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (isVowel(ch)) {
                int index = ch - 'a';
                count[index]++;
                if (first[index] == -1) {
                    first[index] = i;
                }
            }
        }

        List<Character> vowels = new ArrayList<>();
        for (char ch : new char[] {'a', 'e', 'i', 'o', 'u'}) {
            if (count[ch - 'a'] > 0) {
                vowels.add(ch);
            }
        }
        vowels.sort((a, b) -> {
            int ca = count[a - 'a'];
            int cb = count[b - 'a'];
            if (ca != cb) {
                return Integer.compare(cb, ca);
            }
            return Integer.compare(first[a - 'a'], first[b - 'a']);
        });

        List<Character> stream = new ArrayList<>();
        for (char ch : vowels) {
            for (int i = 0; i < count[ch - 'a']; i++) {
                stream.add(ch);
            }
        }

        char[] chars = s.toCharArray();
        int ptr = 0;
        for (int i = 0; i < chars.length; i++) {
            if (isVowel(chars[i])) {
                chars[i] = stream.get(ptr++);
            }
        }
        return new String(chars);
    }

    private boolean isVowel(char ch) {
        return ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u';
    }
}
// @lc code=end
