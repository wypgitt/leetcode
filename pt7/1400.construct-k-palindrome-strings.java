/*
 * LeetCode 1400 - Construct K Palindrome Strings
 */
class Solution {
    public boolean canConstruct(String s, int k) {
        if (k > s.length()) {
            return false;
        }

        int[] counts = new int[26];
        for (int i = 0; i < s.length(); i++) {
            counts[s.charAt(i) - 'a']++;
        }

        int oddCount = 0;
        for (int count : counts) {
            if (count % 2 == 1) {
                oddCount++;
            }
        }

        return oddCount <= k;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Each palindrome can contain at most one odd-frequency character. If the
 * string has `oddCount` characters with odd frequency, we need at least
 * `oddCount` palindromes. We also cannot create more non-empty palindromes than
 * there are characters, so k must be <= s.length().
 *
 * Java data structures:
 * `int[26]` counts lowercase letters. Only parity matters, but full counts make
 * the explanation direct.
 *
 * Why condition is sufficient:
 * Once odd characters have centers, all even leftovers can be paired into
 * palindromes or split further to reach any k up to the string length.
 *
 * Edge cases:
 * - k > length is impossible.
 * - k == length is always possible, one character per palindrome.
 * - All even counts means oddCount is 0, so any feasible k works.
 *
 * Complexity:
 * Time O(n).
 * Space O(1), exactly 26 counters.
 */
