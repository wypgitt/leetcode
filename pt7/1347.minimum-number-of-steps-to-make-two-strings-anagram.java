/*
 * LeetCode 1347 - Minimum Number of Steps to Make Two Strings Anagram
 */
class Solution {
    public int minSteps(String s, String t) {
        int[] balance = new int[26];

        for (int i = 0; i < s.length(); i++) {
            balance[s.charAt(i) - 'a']++;
            balance[t.charAt(i) - 'a']--;
        }

        int steps = 0;
        for (int count : balance) {
            if (count > 0) {
                steps += count;
            }
        }

        return steps;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * We can replace characters in t. Count which characters s needs and subtract
 * what t already has. Positive balances are characters still missing from t;
 * each missing character requires one replacement.
 *
 * Java data structures:
 * `int[26]` is better than a map here because strings contain only lowercase
 * English letters. It is compact and constant-size.
 *
 * Edge cases:
 * - Already anagrams produce all zero balances.
 * - Negative balances mean t has extra characters that can be replaced.
 * - Repeated letters are counted by frequency, not just existence.
 *
 * Complexity:
 * Time O(n).
 * Space O(1), exactly 26 counters.
 */
