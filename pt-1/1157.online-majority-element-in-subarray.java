/*
 * @lc app=leetcode id=1157 lang=java
 *
 * [1157] Online Majority Element In Subarray
 */

/*
 * --- Interview notes (majority + segment tree merge, verification, complexity, constraints, alternatives) ---
 *
 * Problem
 * Preprocess array `arr`. Each query(left, right, threshold) asks: is there a value that appears **at least**
 * `threshold` times in arr[left..right] inclusive? Return such a value, or -1. Up to 1e4 queries on |arr| <= 2e4.
 *
 * Constraint (critical)
 * `2 * threshold > (right - left + 1)` i.e. threshold > half the subarray length. So any valid answer would have to be a
 * **strict majority** in the usual sense (more than half). At most one distinct value can satisfy the frequency check.
 *
 * Why not scan each query in O(range length)?
 * Worst-case O(queries * n) is too slow for n, queries ~ 1e4–2e4.
 *
 * Plan — two phases
 * (1) **Candidate** x that *could* be the majority on [L, R], in O(log n) time.
 * (2) **Verify** frequency of x on [L, R], in O(log n) time. If count >= threshold return x else -1.
 *
 * Phase 1 — Boyer–Moore majority merge on a segment tree
 * Boyer–Moore voting finds a majority element in one pass if one exists (> n/2 copies). For subarrays we cannot afford a
 * linear scan per query. Observation: the same “candidate + relative count” pairing can be **merged** like associative
 * folds over contiguous blocks (same idea as parallel BM).
 *
 * Merge two adjacent intervals with summaries (v1, c1) and (v2, c2):
 *   • If v1 == v2 → (v1, c1 + c2)
 *   • Else if c1 > c2 → (v1, c1 - c2)   # cancel opposing votes
 *   • Else → (v2, c2 - c1)
 * Leaves store (arr[i], 1). Internal nodes merge children. Range query merges O(log n) canonical segments → O(log n).
 *
 * If a strict majority exists on [L,R], its value is **always** the candidate produced by this merge (standard fact).
 * If no majority exists, the candidate is arbitrary garbage for our purpose — verification fails.
 *
 * Phase 2 — Frequency via sorted positions per value
 * Build `pos[value] = sorted list of indices where arr[index] == value`. Count of value x in [L,R] is:
 *   bisect_right(pos[x], R) - bisect_left(pos[x], L)   → O(log n) per query.
 *
 * Why this data structure for verification?
 * • Values up to 20000 — coarse bucket map is fine.
 * • Sorted indices + bisect beats scanning and pairs naturally with offline preprocessing O(n).
 *
 * Time complexity
 * • Build positions map: O(n). Build segment tree: O(n).
 * • Each query: O(log n) segment-tree walk + O(log n) bisects → **O(log n)**.
 *
 * Space complexity
 * • Positions store each index once: O(n). Segment tree ~4n nodes: **O(n)**.
 *
 * Edge cases
 * • threshold equals subarray length → verify candidate count == length.
 * • No majority / frequency below threshold → verification returns -1 even if candidate looks plausible after BM merge.
 *
 * Tests (statement)
 * arr = [1,1,2,2,1,1]
 * query(0,5,4) → value 1 appears 4 times → 1
 * query(0,3,3) → no value ≥ 3 times in [1,1,2,2] → -1
 * query(2,3,2) → [2,2] → 2
 *
 * Alternative approaches (trade-offs)
 * • **Random sampling** (problem hints): sample random indices in [L,R]; check arr[k]. Probability ≥ 1/2 each trial if a
 *   majority exists; repeat ~40–60 times for negligible failure — expected O(k log n) per query with verification. Randomized,
 *   not deterministic.
 * • **Wavelet tree / persistent structures**: heavier; overkill for interviews unless already familiar.
 * • **Square decomposition**: O(√n) or similar per query.
 *
 * Improvements
 * • Iterative segment tree to avoid recursion overhead (same asymptotics).
 * • Single bisect on `pos[candidate]` after query.
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MajorityChecker {

    private final int[] arr;
    private final int n;
    private final Map<Integer, List<Integer>> pos;
    private final int[] treeVal;
    private final int[] treeCnt;

    private int[] merge(int[] a, int[] b) {
        int v1 = a[0];
        int c1 = a[1];
        int v2 = b[0];
        int c2 = b[1];
        if (v1 == v2) {
            return new int[] {v1, c1 + c2};
        }
        if (c1 > c2) {
            return new int[] {v1, c1 - c2};
        }
        return new int[] {v2, c2 - c1};
    }

    private void build(int node, int l, int r) {
        if (l == r) {
            treeVal[node] = arr[l];
            treeCnt[node] = 1;
            return;
        }
        int m = (l + r) >>> 1;
        build(node * 2, l, m);
        build(node * 2 + 1, m + 1, r);
        int[] merged = merge(new int[] {treeVal[node * 2], treeCnt[node * 2]}, new int[] {treeVal[node * 2 + 1], treeCnt[node * 2 + 1]});
        treeVal[node] = merged[0];
        treeCnt[node] = merged[1];
    }

    private int[] query(int node, int l, int r, int ql, int qr) {
        if (ql <= l && r <= qr) {
            return new int[] {treeVal[node], treeCnt[node]};
        }
        if (r < ql || l > qr) {
            return new int[] {0, 0};
        }
        int m = (l + r) >>> 1;
        int[] left = query(node * 2, l, m, ql, qr);
        int[] right = query(node * 2 + 1, m + 1, r, ql, qr);
        return merge(left, right);
    }

    private static int lowerBound(List<Integer> list, int x) {
        int lo = 0;
        int hi = list.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (list.get(mid) < x) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }

    private static int upperBound(List<Integer> list, int x) {
        int lo = 0;
        int hi = list.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (list.get(mid) <= x) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }

    public MajorityChecker(int[] arr) {
        this.arr = arr;
        this.n = arr.length;
        this.pos = new HashMap<>();
        for (int i = 0; i < n; i++) {
            pos.computeIfAbsent(arr[i], k -> new ArrayList<>()).add(i);
        }
        this.treeVal = new int[4 * n + 4];
        this.treeCnt = new int[4 * n + 4];
        build(1, 0, n - 1);
    }

    public int query(int left, int right, int threshold) {
        int[] cand = query(1, 0, n - 1, left, right);
        int x = cand[0];
        List<Integer> lst = pos.getOrDefault(x, Collections.emptyList());
        int cnt = upperBound(lst, right) - lowerBound(lst, left);
        return cnt >= threshold ? x : -1;
    }
}

/*
Your MajorityChecker object will be instantiated and called as such:
MajorityChecker obj = new MajorityChecker(arr);
int param_1 = obj.query(left,right,threshold);
*/
// @lc code=end
