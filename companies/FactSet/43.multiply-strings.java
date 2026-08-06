/**
 * Algorithm:
 * Simulate grade-school multiplication. Digits at num1[i] and num2[j] add to
 * result positions i + j and i + j + 1 in a length m + n digit array.
 *
 * Java data structures:
 * int[] accumulates per-position digits and carries without converting the full
 * input strings to integers.
 *
 * Complexity:
 * Time O(mn), space O(m + n).
 */
class Solution {
    public String multiply(String num1, String num2) {
        if (num1.equals("0") || num2.equals("0")) {
            return "0";
        }
        int m = num1.length();
        int n = num2.length();
        int[] res = new int[m + n];
        for (int i = m - 1; i >= 0; i--) {
            for (int j = n - 1; j >= 0; j--) {
                int product = (num1.charAt(i) - '0') * (num2.charAt(j) - '0');
                int total = product + res[i + j + 1];
                res[i + j + 1] = total % 10;
                res[i + j] += total / 10;
            }
        }
        StringBuilder ans = new StringBuilder();
        int start = 0;
        while (start < res.length && res[start] == 0) {
            start++;
        }
        for (int i = start; i < res.length; i++) {
            ans.append(res[i]);
        }
        return ans.toString();
    }
}

