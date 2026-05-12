import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

class Solution {
    public List<List<Integer>> reconstructMatrix(int upper, int lower, int[] colsum) {
        Integer[] top = new Integer[colsum.length];
        Integer[] bottom = new Integer[colsum.length];
        Arrays.fill(top, 0);
        Arrays.fill(bottom, 0);

        for (int i = 0; i < colsum.length; i++) {
            if (colsum[i] == 2) {
                top[i] = 1;
                bottom[i] = 1;
                upper--;
                lower--;
            }
        }
        if (upper < 0 || lower < 0) {
            return Collections.emptyList();
        }

        for (int i = 0; i < colsum.length; i++) {
            if (colsum[i] == 1) {
                if (upper > 0) {
                    top[i] = 1;
                    upper--;
                } else if (lower > 0) {
                    bottom[i] = 1;
                    lower--;
                } else {
                    return Collections.emptyList();
                }
            }
        }

        if (upper != 0 || lower != 0) {
            return Collections.emptyList();
        }

        List<List<Integer>> ans = new ArrayList<>();
        ans.add(Arrays.asList(top));
        ans.add(Arrays.asList(bottom));
        return ans;
    }
}

/*
Explanation

Columns with colsum 2 are forced to be [1, 1], so assign those first and reduce
both row budgets. Columns with colsum 1 can go to either row, so place them in
the upper row while it still needs ones, then in the lower row.

The greedy choice is safe because all remaining single-one columns are
interchangeable; only the remaining row sums matter.

Edge cases: too many forced 2 columns; not enough single-one columns; leftover
upper or lower budget after assignment.

Time complexity: O(n).
Space complexity: O(n) for the output rows.
*/
