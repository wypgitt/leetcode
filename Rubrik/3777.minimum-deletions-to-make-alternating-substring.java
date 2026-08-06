/*
 * @lc app=leetcode id=3777 lang=java
 *
 * [3777] Minimum Deletions to Make Alternating Substring
 *
 * In a binary substring, the longest alternating subsequence keeps one
 * character per run. So deletions = length - runs, and runs are
 * 1 + number of adjacent transitions. A Fenwick tree stores transition flags
 * and point updates after flips.
 *
 * Java note: Fenwick tree gives O(log n) update and range-sum queries over the
 * n - 1 adjacency edges.
 *
 * Time: O((n + q) log n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public int[] minDeletions(String s, int[][] queries) {
        char[] chars = s.toCharArray();
        int n = chars.length;
        Fenwick fenwick = new Fenwick(Math.max(1, n - 1));

        for (int i = 0; i < n - 1; i++) {
            if (edgeValue(chars, i) == 1) {
                fenwick.add(i, 1);
            }
        }

        List<Integer> out = new ArrayList<>();
        for (int[] query : queries) {
            if (query[0] == 1) {
                int index = query[1];
                int leftOld = index > 0 ? edgeValue(chars, index - 1) : 0;
                int rightOld = index < n - 1 ? edgeValue(chars, index) : 0;

                chars[index] = chars[index] == 'A' ? 'B' : 'A';
                refreshEdge(chars, fenwick, index - 1, leftOld);
                refreshEdge(chars, fenwick, index, rightOld);
            } else {
                int left = query[1];
                int right = query[2];
                int transitions = fenwick.rangeSum(left, right - 1);
                int length = right - left + 1;
                out.add(length - (transitions + 1));
            }
        }

        int[] answer = new int[out.size()];
        for (int i = 0; i < out.size(); i++) {
            answer[i] = out.get(i);
        }
        return answer;
    }

    private int edgeValue(char[] chars, int index) {
        return chars[index] != chars[index + 1] ? 1 : 0;
    }

    private void refreshEdge(char[] chars, Fenwick fenwick, int index, int oldValue) {
        if (index < 0 || index >= chars.length - 1) {
            return;
        }
        int newValue = edgeValue(chars, index);
        if (newValue != oldValue) {
            fenwick.add(index, newValue - oldValue);
        }
    }

    private static class Fenwick {
        private final int size;
        private final int[] tree;

        Fenwick(int size) {
            this.size = size;
            this.tree = new int[size + 1];
        }

        void add(int index, int delta) {
            index++;
            while (index <= size) {
                tree[index] += delta;
                index += index & -index;
            }
        }

        int rangeSum(int left, int right) {
            if (left > right) {
                return 0;
            }
            return prefixSum(right) - (left == 0 ? 0 : prefixSum(left - 1));
        }

        private int prefixSum(int index) {
            int total = 0;
            index++;
            while (index > 0) {
                total += tree[index];
                index -= index & -index;
            }
            return total;
        }
    }
}
// @lc code=end
