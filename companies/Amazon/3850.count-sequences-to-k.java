/*
 * @lc app=leetcode id=3850 lang=java
 *
 * [3850] Count Sequences to K
 *
 * Factor k and each number by primes 2, 3, and 5. Each number may be skipped,
 * multiplied, or divided, so DP counts reachable exponent triples. If k has
 * any other prime factor, it is unreachable.
 *
 * Java note: State is an immutable triple with equals/hashCode so HashMap can
 * serve as Python's Counter over tuples.
 *
 * Time: O(n * states). Space: O(states).
 */

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

// @lc code=start
class Solution {
    public long countSequences(int[] nums, int k) {
        FactorResult target = factorTarget(k);
        if (!target.reachable) {
            return 0;
        }

        Map<State, Long> dp = new HashMap<>();
        dp.put(new State(0, 0, 0), 1L);

        for (int num : nums) {
            int[] delta = factorSmall(num);
            Map<State, Long> next = new HashMap<>();
            for (Map.Entry<State, Long> entry : dp.entrySet()) {
                State s = entry.getKey();
                long ways = entry.getValue();
                add(next, s, ways);
                add(next, new State(s.a + delta[0], s.b + delta[1], s.c + delta[2]), ways);
                add(next, new State(s.a - delta[0], s.b - delta[1], s.c - delta[2]), ways);
            }
            dp = next;
        }

        return dp.getOrDefault(target.state, 0L);
    }

    private void add(Map<State, Long> map, State state, long ways) {
        map.put(state, map.getOrDefault(state, 0L) + ways);
    }

    private FactorResult factorTarget(int value) {
        int[] exponents = factorSmall(value);
        for (int prime : new int[] {2, 3, 5}) {
            while (value % prime == 0) {
                value /= prime;
            }
        }
        return new FactorResult(new State(exponents[0], exponents[1], exponents[2]), value == 1);
    }

    private int[] factorSmall(int value) {
        int[] exponents = new int[3];
        int[] primes = {2, 3, 5};
        for (int i = 0; i < 3; i++) {
            while (value % primes[i] == 0) {
                value /= primes[i];
                exponents[i]++;
            }
        }
        return exponents;
    }

    private static class FactorResult {
        final State state;
        final boolean reachable;

        FactorResult(State state, boolean reachable) {
            this.state = state;
            this.reachable = reachable;
        }
    }

    private static class State {
        final int a;
        final int b;
        final int c;

        State(int a, int b, int c) {
            this.a = a;
            this.b = b;
            this.c = c;
        }

        @Override
        public boolean equals(Object obj) {
            if (!(obj instanceof State)) {
                return false;
            }
            State other = (State) obj;
            return a == other.a && b == other.b && c == other.c;
        }

        @Override
        public int hashCode() {
            return Objects.hash(a, b, c);
        }
    }
}
// @lc code=end
