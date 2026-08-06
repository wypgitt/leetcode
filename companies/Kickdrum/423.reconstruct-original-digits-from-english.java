/**
 * Algorithm:
 * Count letters, then recover digits with unique identifying letters:
 * z->0, w->2, u->4, x->6, g->8. The remaining digit counts are derived after
 * subtracting those already fixed digits.
 *
 * Java data structures:
 * Fixed int arrays replace Python Counter. The alphabet and digit set are
 * constant size, so access is O(1).
 *
 * Complexity:
 * Time O(n), auxiliary space O(1).
 */
class Solution {
    public String originalDigits(String s) {
        int[] count = new int[26];
        for (int i = 0; i < s.length(); i++) {
            count[s.charAt(i) - 'a']++;
        }

        int[] digit = new int[10];
        digit[0] = count['z' - 'a'];
        digit[2] = count['w' - 'a'];
        digit[4] = count['u' - 'a'];
        digit[6] = count['x' - 'a'];
        digit[8] = count['g' - 'a'];
        digit[3] = count['h' - 'a'] - digit[8];
        digit[5] = count['f' - 'a'] - digit[4];
        digit[7] = count['s' - 'a'] - digit[6];
        digit[1] = count['o' - 'a'] - digit[0] - digit[2] - digit[4];
        digit[9] = count['i' - 'a'] - digit[5] - digit[6] - digit[8];

        StringBuilder ans = new StringBuilder();
        for (int i = 0; i < 10; i++) {
            for (int c = 0; c < digit[i]; c++) {
                ans.append(i);
            }
        }
        return ans.toString();
    }
}

