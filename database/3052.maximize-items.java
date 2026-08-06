/*
 * @lc app=leetcode id=3052 lang=java
 *
 * [3052] Maximize Items
 *
 * <p>LeetCode lists this as a SQL problem. This mirrors the editorial arithmetic in Java using {@link
 * java.math.BigDecimal}.
 */

// @lc code=start
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

class Solution {
    private static final BigDecimal WAREHOUSE = new BigDecimal("500000");

    public List<List<String>> maximizeItems(String[] itemType, BigDecimal[] squareFootage) {
        BigDecimal primeSum = BigDecimal.ZERO;
        int primeCnt = 0;
        BigDecimal notSum = BigDecimal.ZERO;
        int notCnt = 0;
        for (int i = 0; i < itemType.length; i++) {
            BigDecimal a = squareFootage[i];
            if ("prime_eligible".equals(itemType[i])) {
                primeSum = primeSum.add(a);
                primeCnt++;
            } else {
                notSum = notSum.add(a);
                notCnt++;
            }
        }
        BigDecimal s = primeSum;
        long primeItems = 0;
        BigDecimal rem;
        if (primeCnt == 0) {
            rem = WAREHOUSE;
        } else {
            BigDecimal sets = WAREHOUSE.divideToIntegralValue(s);
            rem = WAREHOUSE.remainder(s);
            primeItems = sets.multiply(BigDecimal.valueOf(primeCnt)).longValue();
        }
        long notItems = 0;
        if (notCnt > 0 && notSum.signum() > 0) {
            BigDecimal setsNot = rem.divideToIntegralValue(notSum);
            notItems = setsNot.multiply(BigDecimal.valueOf(notCnt)).longValue();
        }
        List<List<String>> out = new ArrayList<>();
        List<String> row1 = new ArrayList<>();
        row1.add("prime_eligible");
        row1.add(String.valueOf(primeItems));
        out.add(row1);
        List<String> row2 = new ArrayList<>();
        row2.add("not_prime");
        row2.add(String.valueOf(notItems));
        out.add(row2);
        return out;
    }
}
// @lc code=end
