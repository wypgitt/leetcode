import java.util.*;

/**
 * Algorithm:
 * Long division with remainder tracking. When a remainder repeats, the decimal
 * digits from its first position repeat, so insert parentheses there.
 *
 * Java data structures:
 * HashMap<Long, Integer> maps a remainder to its position in StringBuilder.
 * long avoids overflow for Integer.MIN_VALUE absolute values.
 *
 * Complexity:
 * Time O(number of produced digits), space O(number of distinct remainders).
 */
class Solution {
    public String fractionToDecimal(int numerator, int denominator) {
        if (numerator == 0) {
            return "0";
        }
        StringBuilder out = new StringBuilder();
        if ((numerator < 0) ^ (denominator < 0)) {
            out.append('-');
        }
        long n = Math.abs((long) numerator);
        long d = Math.abs((long) denominator);
        out.append(n / d);
        long rem = n % d;
        if (rem == 0) {
            return out.toString();
        }
        out.append('.');
        Map<Long, Integer> seen = new HashMap<>();
        while (rem != 0) {
            if (seen.containsKey(rem)) {
                int idx = seen.get(rem);
                out.insert(idx, '(');
                out.append(')');
                break;
            }
            seen.put(rem, out.length());
            rem *= 10;
            out.append(rem / d);
            rem %= d;
        }
        return out.toString();
    }
}

