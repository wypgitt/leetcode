/*
 * @lc app=leetcode id=2701 lang=java
 *
 * [2701] Consecutive Transactions with Increasing Amounts
 *
 * <p>LeetCode lists this as a database (SQL) problem. This file mirrors the same logic in Java for
 * local practice: rows are (customer_id, transaction_date as epoch-day or ISO string, amount).
 */

// @lc code=start
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class Solution {

    static class Txn {
        final int customerId;
        final LocalDate date;
        final int amount;

        Txn(int customerId, LocalDate date, int amount) {
            this.customerId = customerId;
            this.date = date;
            this.amount = amount;
        }
    }

    /**
     * @return rows [customer_id, consecutive_start ISO, consecutive_end ISO], sorted like the statement.
     */
    public List<List<String>> consecutiveIncreasingRanges(List<Txn> transactions) {
        transactions.sort(Comparator.comparingInt((Txn t) -> t.customerId).thenComparing(t -> t.date));
        List<List<String>> out = new ArrayList<>();
        int i = 0;
        int n = transactions.size();
        while (i < n) {
            int cid = transactions.get(i).customerId;
            int j = i;
            while (j < n && transactions.get(j).customerId == cid) {
                j++;
            }
            List<Txn> slice = transactions.subList(i, j);
            findRangesForCustomer(cid, slice, out);
            i = j;
        }
        out.sort(Comparator.comparing((List<String> r) -> Integer.parseInt(r.get(0)))
                .thenComparing(r -> r.get(1))
                .thenComparing(r -> r.get(2)));
        return out;
    }

    private void findRangesForCustomer(int cid, List<Txn> rows, List<List<String>> out) {
        int runStart = 0;
        for (int p = 1; p <= rows.size(); p++) {
            boolean extend =
                    p < rows.size()
                            && ChronoUnit.DAYS.between(rows.get(p - 1).date, rows.get(p).date) == 1
                            && rows.get(p).amount > rows.get(p - 1).amount;
            if (!extend) {
                int len = p - runStart;
                if (len >= 3) {
                    List<String> r = new ArrayList<>(3);
                    r.add(String.valueOf(cid));
                    r.add(rows.get(runStart).date.toString());
                    r.add(rows.get(p - 1).date.toString());
                    out.add(r);
                }
                runStart = p;
            }
        }
    }

    /** Convenience: parse yyyy-MM-dd dates. */
    public List<List<String>> consecutiveIncreasingRangesParsed(
            int[] customerId, String[] dates, int[] amount) {
        List<Txn> list = new ArrayList<>();
        for (int i = 0; i < customerId.length; i++) {
            list.add(new Txn(customerId[i], LocalDate.parse(dates[i]), amount[i]));
        }
        return consecutiveIncreasingRanges(list);
    }
}
// @lc code=end
