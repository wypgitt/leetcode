/*
 * LeetCode 1328 - Break a Palindrome
 */
class Solution {
    public String breakPalindrome(String palindrome) {
        if (palindrome.length() == 1) {
            return "";
        }

        char[] chars = palindrome.toCharArray();
        for (int i = 0; i < chars.length / 2; i++) {
            if (chars[i] != 'a') {
                chars[i] = 'a';
                return new String(chars);
            }
        }

        chars[chars.length - 1] = 'b';
        return new String(chars);
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * To get the lexicographically smallest result, change the earliest possible
 * non-'a' character in the first half to 'a'. We only inspect the first half
 * because changing the mirrored second-half character would produce a larger
 * string. If the first half is all 'a', change the last character to 'b'.
 *
 * Edge cases:
 * - Length 1 cannot be changed into a non-palindrome, so return "".
 * - Odd-length center character is skipped because changing only the center
 *   would keep the string a palindrome.
 * - All 'a' strings become something like "aaab".
 *
 * Complexity:
 * Time O(n).
 * Space O(n), because Java strings are immutable and we use a char array.
 */
