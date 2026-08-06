/**
 * Algorithm:
 * Scan signed fractions one by one, merge with the running fraction using a
 * common denominator, and reduce by gcd after every merge.
 *
 * Complexity:
 * Time O(n log V), where gcd is logarithmic in value size. Space O(1).
 */
class Solution {
    public String fractionAddition(String expression) {
        int numerator = 0;
        int denominator = 1;
        int i = 0;
        while (i < expression.length()) {
            int sign = 1;
            if (expression.charAt(i) == '+' || expression.charAt(i) == '-') {
                sign = expression.charAt(i) == '-' ? -1 : 1;
                i++;
            }
            int n = 0;
            while (Character.isDigit(expression.charAt(i))) {
                n = n * 10 + expression.charAt(i) - '0';
                i++;
            }
            i++;
            int d = 0;
            while (i < expression.length() && Character.isDigit(expression.charAt(i))) {
                d = d * 10 + expression.charAt(i) - '0';
                i++;
            }
            n *= sign;
            numerator = numerator * d + n * denominator;
            denominator *= d;
            int g = gcd(Math.abs(numerator), denominator);
            numerator /= g;
            denominator /= g;
        }
        return numerator + "/" + denominator;
    }

    private int gcd(int a, int b) {
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }
        return a;
    }
}

