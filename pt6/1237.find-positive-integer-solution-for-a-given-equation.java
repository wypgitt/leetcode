import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/*
class CustomFunction {
    public int f(int x, int y);
}
*/

class Solution {
    public List<List<Integer>> findSolution(CustomFunction customfunction, int z) {
        List<List<Integer>> ans = new ArrayList<>();
        int x = 1;
        int y = 1000;

        while (x <= 1000 && y >= 1) {
            int value = customfunction.f(x, y);
            if (value == z) {
                ans.add(Arrays.asList(x, y));
                x++;
                y--;
            } else if (value < z) {
                x++;
            } else {
                y--;
            }
        }

        return ans;
    }
}

/*
Explanation

The function is strictly increasing in both x and y. Treat the search space as
a sorted matrix and start at the top-right corner: x = 1, y = 1000. If the
value is too small, increase x. If it is too large, decrease y. On equality,
record the pair and move both because strict monotonicity prevents another
solution with the same x or y.

This avoids checking all one million pairs.

Edge cases: no solution; boundary solutions; multiple solutions along the
monotone frontier.

Time complexity: O(1000), generally O(limit).
Space complexity: O(1) besides the output.
*/
