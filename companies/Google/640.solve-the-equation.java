/**
 * Algorithm:
 * Parse each side into (x coefficient, constant). Move x terms to the left and
 * constants to the right, then solve coeff * x = constant.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public String solveEquation(String equation) {
        String[] sides = equation.split("=");
        int[] left = parse(sides[0]);
        int[] right = parse(sides[1]);
        int coeff = left[0] - right[0];
        int constant = right[1] - left[1];
        if (coeff == 0) {
            return constant == 0 ? "Infinite solutions" : "No solution";
        }
        return "x=" + (constant / coeff);
    }

    private int[] parse(String side) {
        int coeff = 0;
        int constant = 0;
        int i = 0;
        int sign = 1;
        while (i < side.length()) {
            char ch = side.charAt(i);
            if (ch == '+') {
                sign = 1;
                i++;
            } else if (ch == '-') {
                sign = -1;
                i++;
            } else {
                int j = i;
                while (j < side.length() && Character.isDigit(side.charAt(j))) {
                    j++;
                }
                int num = j > i ? Integer.parseInt(side.substring(i, j)) : 1;
                if (j < side.length() && side.charAt(j) == 'x') {
                    coeff += sign * num;
                    j++;
                } else {
                    constant += sign * num;
                }
                i = j;
            }
        }
        return new int[] {coeff, constant};
    }
}

