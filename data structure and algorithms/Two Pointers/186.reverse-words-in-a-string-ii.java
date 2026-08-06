/**
 * Algorithm:
 * Reverse the entire character array, then reverse each individual word. This
 * changes word order in place while preserving each word's letters.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public void reverseWords(char[] s) {
        reverse(s, 0, s.length - 1);
        int start = 0;
        for (int i = 0; i <= s.length; i++) {
            if (i == s.length || s[i] == ' ') {
                reverse(s, start, i - 1);
                start = i + 1;
            }
        }
    }

    private void reverse(char[] s, int left, int right) {
        while (left < right) {
            char tmp = s[left];
            s[left++] = s[right];
            s[right--] = tmp;
        }
    }
}

