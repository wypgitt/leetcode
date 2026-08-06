import java.util.*;

/**
 * Algorithm:
 * Backtrack over possible next numbers. After two values are chosen, the next
 * value is forced to equal their sum, which prunes most branches. Stop a branch
 * on leading zeros, values above Integer.MAX_VALUE, or values above the
 * expected Fibonacci sum.
 *
 * Java data structures:
 * ArrayList<Integer> stores the current path and final answer.
 *
 * Complexity:
 * The first two numbers determine the rest, so practical time is O(n^2) split
 * choices with O(n) recursion/output space.
 */
class Solution {
    private static final long LIMIT = Integer.MAX_VALUE;
    private String num;
    private List<Integer> ans;

    public List<Integer> splitIntoFibonacci(String num) {
        this.num = num;
        this.ans = new ArrayList<>();
        dfs(0);
        return ans;
    }

    private boolean dfs(int pos) {
        if (pos == num.length()) {
            return ans.size() >= 3;
        }
        long value = 0;
        for (int end = pos; end < num.length(); end++) {
            if (end > pos && num.charAt(pos) == '0') {
                break;
            }
            value = value * 10 + num.charAt(end) - '0';
            if (value > LIMIT) {
                break;
            }
            if (ans.size() >= 2) {
                long expected = (long) ans.get(ans.size() - 1) + ans.get(ans.size() - 2);
                if (value < expected) {
                    continue;
                }
                if (value > expected) {
                    break;
                }
            }
            ans.add((int) value);
            if (dfs(end + 1)) {
                return true;
            }
            ans.remove(ans.size() - 1);
        }
        return false;
    }
}

