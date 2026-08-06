import java.util.*;

/**
 * Algorithm:
 * Backtrack by assigning the longest remaining matchstick to one of four side
 * sums. Sorting descending prunes early. Equal side sums are skipped at each
 * level to avoid symmetric duplicate states.
 *
 * Java data structures:
 * int[4] stores the partial side lengths; HashSet<Integer> skips duplicate
 * side states in the same recursion frame.
 *
 * Complexity:
 * Worst-case exponential, bounded by O(4^n), with O(n) recursion space.
 */
class Solution {
    private int[] matchsticks;
    private int[] sides;
    private int side;

    public boolean makesquare(int[] matchsticks) {
        int total = 0;
        for (int x : matchsticks) {
            total += x;
        }
        if (matchsticks.length < 4 || total % 4 != 0) {
            return false;
        }
        side = total / 4;
        Arrays.sort(matchsticks);
        reverse(matchsticks);
        if (matchsticks[0] > side) {
            return false;
        }
        this.matchsticks = matchsticks;
        sides = new int[4];
        return dfs(0);
    }

    private boolean dfs(int i) {
        if (i == matchsticks.length) {
            return sides[0] == side && sides[1] == side && sides[2] == side && sides[3] == side;
        }
        int length = matchsticks[i];
        Set<Integer> seen = new HashSet<>();
        for (int j = 0; j < 4; j++) {
            if (seen.contains(sides[j]) || sides[j] + length > side) {
                continue;
            }
            seen.add(sides[j]);
            sides[j] += length;
            if (dfs(i + 1)) {
                return true;
            }
            sides[j] -= length;
        }
        return false;
    }

    private void reverse(int[] a) {
        for (int l = 0, r = a.length - 1; l < r; l++, r--) {
            int tmp = a[l];
            a[l] = a[r];
            a[r] = tmp;
        }
    }
}

