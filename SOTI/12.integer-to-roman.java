/**
 * Algorithm:
 * Greedily append the largest Roman symbol value that fits the remaining
 * number. Including subtractive forms such as CM, CD, XC, XL, IX, and IV makes
 * the greedy choice valid for every digit group.
 *
 * Java data structures:
 * Parallel arrays store values and symbols in descending order; StringBuilder
 * avoids repeated immutable string concatenation.
 *
 * Complexity:
 * O(1) time and space because the input range is fixed.
 */
class Solution {
    public String intToRoman(int num) {
        int[] values = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
        String[] symbols = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};
        StringBuilder ans = new StringBuilder();
        for (int i = 0; i < values.length; i++) {
            while (num >= values[i]) {
                ans.append(symbols[i]);
                num -= values[i];
            }
        }
        return ans.toString();
    }
}

