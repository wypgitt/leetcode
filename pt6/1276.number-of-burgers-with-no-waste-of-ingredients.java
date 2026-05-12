import java.util.Arrays;
import java.util.Collections;
import java.util.List;

class Solution {
    public List<Integer> numOfBurgers(int tomatoSlices, int cheeseSlices) {
        int extraTomatoes = tomatoSlices - 2 * cheeseSlices;
        if (extraTomatoes < 0 || extraTomatoes % 2 != 0) {
            return Collections.emptyList();
        }

        int jumbo = extraTomatoes / 2;
        int small = cheeseSlices - jumbo;
        if (small < 0) {
            return Collections.emptyList();
        }

        return Arrays.asList(jumbo, small);
    }
}

/*
Explanation

Let jumbo = x and small = y. Then x + y = cheeseSlices and
4x + 2y = tomatoSlices. Subtracting 2 * cheeseSlices from tomatoSlices leaves
2x, so x = (tomatoSlices - 2 * cheeseSlices) / 2.

After computing jumbo, small is the remaining cheese count. Both counts must be
nonnegative integers.

Edge cases: too few tomatoes; odd extra tomato count; jumbo greater than total
cheese.

Time complexity: O(1).
Space complexity: O(1).
*/
