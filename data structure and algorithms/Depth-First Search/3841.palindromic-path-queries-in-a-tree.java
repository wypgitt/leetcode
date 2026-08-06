/*
 * @lc app=leetcode id=3841 lang=java
 *
 * [3841] Palindromic Path Queries in a Tree
 *
 * A path can be rearranged into a palindrome iff at most one character has odd
 * frequency. Store each node's character as a bit mask and query path XOR with
 * Heavy-Light Decomposition plus a segment tree; updates are point updates.
 *
 * Java note: segment tree supports range XOR and point assignment in O(log n).
 * HLD decomposes any path into O(log n) contiguous base-array intervals.
 *
 * Time: O((n + q) log^2 n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public boolean[] palindromePath(int n, int[][] edges, String s, String[] queries) {
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
            graph[edge[1]].add(edge[0]);
        }

        int[] parent = new int[n];
        int[] depth = new int[n];
        int[] order = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = -1;
        }
        int ordSize = 0;
        order[ordSize++] = 0;
        for (int i = 0; i < ordSize; i++) {
            int node = order[i];
            for (int nei : graph[node]) {
                if (nei == parent[node]) {
                    continue;
                }
                parent[nei] = node;
                depth[nei] = depth[node] + 1;
                order[ordSize++] = nei;
            }
        }

        int[] size = new int[n];
        int[] heavy = new int[n];
        for (int i = 0; i < n; i++) {
            size[i] = 1;
            heavy[i] = -1;
        }
        for (int i = n - 1; i >= 0; i--) {
            int node = order[i];
            int bestSize = 0;
            for (int nei : graph[node]) {
                if (parent[nei] == node) {
                    size[node] += size[nei];
                    if (size[nei] > bestSize) {
                        bestSize = size[nei];
                        heavy[node] = nei;
                    }
                }
            }
        }

        int[] head = new int[n];
        int[] pos = new int[n];
        int[] base = new int[n];
        int[] stackNode = new int[n];
        int[] stackHead = new int[n];
        int stackSize = 0;
        int currentPos = 0;
        stackNode[stackSize] = 0;
        stackHead[stackSize++] = 0;

        while (stackSize > 0) {
            int start = stackNode[--stackSize];
            int chainHead = stackHead[stackSize];
            int node = start;
            while (node != -1) {
                head[node] = chainHead;
                pos[node] = currentPos;
                base[currentPos++] = mask(s.charAt(node));

                for (int nei : graph[node]) {
                    if (parent[nei] == node && nei != heavy[node]) {
                        stackNode[stackSize] = nei;
                        stackHead[stackSize++] = nei;
                    }
                }
                node = heavy[node];
            }
        }

        SegmentTreeXor seg = new SegmentTreeXor(base);
        List<Boolean> answers = new ArrayList<>();
        for (String raw : queries) {
            String[] parts = raw.split(" ");
            if ("update".equals(parts[0])) {
                int node = Integer.parseInt(parts[1]);
                seg.update(pos[node], mask(parts[2].charAt(0)));
            } else {
                int u = Integer.parseInt(parts[1]);
                int v = Integer.parseInt(parts[2]);
                int pathMask = pathXor(u, v, head, parent, depth, pos, seg);
                answers.add((pathMask & (pathMask - 1)) == 0);
            }
        }

        boolean[] out = new boolean[answers.size()];
        for (int i = 0; i < answers.size(); i++) {
            out[i] = answers.get(i);
        }
        return out;
    }

    private int pathXor(int u, int v, int[] head, int[] parent, int[] depth, int[] pos, SegmentTreeXor seg) {
        int answer = 0;
        while (head[u] != head[v]) {
            if (depth[head[u]] < depth[head[v]]) {
                int tmp = u;
                u = v;
                v = tmp;
            }
            answer ^= seg.query(pos[head[u]], pos[u]);
            u = parent[head[u]];
        }
        if (depth[u] > depth[v]) {
            int tmp = u;
            u = v;
            v = tmp;
        }
        return answer ^ seg.query(pos[u], pos[v]);
    }

    private int mask(char ch) {
        return 1 << (ch - 'a');
    }

    private static class SegmentTreeXor {
        private final int size;
        private final int[] tree;

        SegmentTreeXor(int[] values) {
            int s = 1;
            while (s < values.length) {
                s <<= 1;
            }
            size = s;
            tree = new int[2 * size];
            for (int i = 0; i < values.length; i++) {
                tree[size + i] = values[i];
            }
            for (int i = size - 1; i > 0; i--) {
                tree[i] = tree[i << 1] ^ tree[i << 1 | 1];
            }
        }

        void update(int index, int value) {
            index += size;
            tree[index] = value;
            index >>= 1;
            while (index > 0) {
                tree[index] = tree[index << 1] ^ tree[index << 1 | 1];
                index >>= 1;
            }
        }

        int query(int left, int right) {
            left += size;
            right += size;
            int answer = 0;
            while (left <= right) {
                if ((left & 1) == 1) {
                    answer ^= tree[left++];
                }
                if ((right & 1) == 0) {
                    answer ^= tree[right--];
                }
                left >>= 1;
                right >>= 1;
            }
            return answer;
        }
    }
}
// @lc code=end
