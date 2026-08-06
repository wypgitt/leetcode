/**
 * Algorithm:
 * Parse each complex number into real and imaginary parts, then apply
 * (a + bi)(c + di) = (ac - bd) + (ad + bc)i.
 *
 * Complexity:
 * Time O(1) for bounded input length, space O(1).
 */
class Solution {
    public String complexNumberMultiply(String num1, String num2) {
        int[] x = parse(num1);
        int[] y = parse(num2);
        int real = x[0] * y[0] - x[1] * y[1];
        int imag = x[0] * y[1] + x[1] * y[0];
        return real + "+" + imag + "i";
    }

    private int[] parse(String num) {
        int plus = num.indexOf('+');
        int real = Integer.parseInt(num.substring(0, plus));
        int imag = Integer.parseInt(num.substring(plus + 1, num.length() - 1));
        return new int[] {real, imag};
    }
}

