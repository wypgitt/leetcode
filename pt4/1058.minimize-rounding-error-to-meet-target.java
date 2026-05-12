import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/*
 * 1058. Minimize Rounding Error to Meet Target
 */
class Solution {
    public String minimizeError(String[] prices, int target) {
        int floorSum = 0;
        List<Integer> fractions = new ArrayList<>();

        for (String price : prices) {
            String[] parts = price.split("\\.");
            int whole = Integer.parseInt(parts[0]);
            int fraction = Integer.parseInt(parts[1]);

            floorSum += whole;
            if (fraction != 0) {
                fractions.add(fraction);
            }
        }

        int ceilingsNeeded = target - floorSum;
        if (ceilingsNeeded < 0 || ceilingsNeeded > fractions.size()) {
            return "-1";
        }

        fractions.sort(Collections.reverseOrder());
        int errorThousandths = 0;
        for (int fraction : fractions) {
            errorThousandths += fraction;
        }

        for (int i = 0; i < ceilingsNeeded; i++) {
            int fraction = fractions.get(i);
            errorThousandths += 1000 - 2 * fraction;
        }

        return String.format("%d.%03d", errorThousandths / 1000, errorThousandths % 1000);
    }
}

/*
Interview Explanation

Core idea:
Start by flooring every price. If the floor sum is short of target by k, then
exactly k non-integer prices must be rounded up. To minimize error, round up
the prices with the largest fractional parts.

Java data structures:
- ArrayList<Integer> stores fractional thousandths.
- Sorting in reverse order chooses the best fractions to ceil.
- All arithmetic is done in integer thousandths to avoid double precision
  formatting issues.

Algorithm:
1. Parse each price into whole and fractional thousandths.
2. Add whole values to floorSum.
3. Store nonzero fractions.
4. ceilingsNeeded = target - floorSum.
5. If that number is impossible, return "-1".
6. Base error is the sum of all fractions when flooring all non-integers.
7. For each chosen ceil fraction f, error changes from f to 1000 - f, so add
   1000 - 2f.
8. Format integer thousandths as three decimal places.

Correctness:
The target fixes exactly how many prices must be ceiled. For fractions a > b,
ceiling a instead of b has smaller error delta because 1000 - 2a <
1000 - 2b. Therefore the optimal choice is to ceil the k largest fractions,
which is exactly what the algorithm does.

Complexity:
Parsing is O(n), sorting is O(n log n), and space is O(n).

Edge cases:
- Target below all-floors or above all-ceilings is impossible.
- Integer prices have no rounding choice and no error.
- Output always has exactly three decimals.
*/
