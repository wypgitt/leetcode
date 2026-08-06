import java.util.*;

/**
 * Algorithm:
 * Divide and conquer on each operator. Compute all possible results for the
 * left and right substrings, combine each pair with the operator, and memoize
 * substring results.
 *
 * Java data structures:
 * HashMap<String, List<Integer>> memoizes expression substring results.
 *
 * Complexity:
 * Exponential output size in the number of operators; memoization avoids
 * recomputing identical substrings.
 */
class Solution {
    private Map<String, List<Integer>> memo;

    public List<Integer> diffWaysToCompute(String expression) {
        memo = new HashMap<>();
        return solve(expression);
    }

    private List<Integer> solve(String expr) {
        if (memo.containsKey(expr)) {
            return memo.get(expr);
        }
        List<Integer> results = new ArrayList<>();
        for (int i = 0; i < expr.length(); i++) {
            char ch = expr.charAt(i);
            if (ch == '+' || ch == '-' || ch == '*') {
                for (int a : solve(expr.substring(0, i))) {
                    for (int b : solve(expr.substring(i + 1))) {
                        if (ch == '+') {
                            results.add(a + b);
                        } else if (ch == '-') {
                            results.add(a - b);
                        } else {
                            results.add(a * b);
                        }
                    }
                }
            }
        }
        if (results.isEmpty()) {
            results.add(Integer.parseInt(expr));
        }
        memo.put(expr, results);
        return results;
    }
}

