// Translated from 3901.good-subsequence-queries.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3901 lang=python3
// #
// # [3901] Good Subsequence Queries
// #
// 
// # @lc code=start
// class Solution:
//     pass
// 
// 
// # @lc code=end
// 
// #
// # @lc app=leetcode id=3901 lang=python3
// #
// # [3901] Good Subsequence Queries
// #
// # --- Notes (problem, math, segment tree, n>6 lemma, complexity, interview) ---
// #
// # Problem restatement
// # Array nums of length n, fixed p. A non-empty subsequence S of nums is GOOD if:
// #   (1) |S| < n  (strictly shorter than full length).
// #   (2) gcd of elements of S equals exactly p.
// # Process queries in order: queries[i] = [ind, val] updates nums[ind] := val (persistent).
// # After EACH update, check whether ANY good subsequence exists in the CURRENT nums.
// # Return how many queries resulted in "yes".
// #
// # Observation: only multiples of p matter
// # If gcd(S) = p, every element of S is divisible by p (since p divides gcd(S)).
// # Elements not divisible by p can never appear in a good subsequence. So we may ignore
// # them for feasibility, except they matter for the LENGTH rule: they let us use a
// # subsequence that does NOT take the full array of multiples.
// #
// # Reparameterize per index
// # At each index i, store 0 if nums[i] is not a multiple of p, else store nums[i].
// # The segment tree keeps GCD of these 16 values in any range; equivalently, GCD of
// # all present multiples of p in that range (since gcd(0, x) = |x| in the usual int gcd).
// # Empty subrange query returns 0; gcd(0, a) = a, which matches "no contribution".
// #
// # Let g = GCD of all stored values (whole array), i.e. GCD of all numbers in nums
// # that are divisible by p.
// # If g != p, no subsequence using only multiples of p can have gcd p (any subsequence
// # of multiples has gcd divisible by g, and if g > p or g not multiple... actually
// # if g is not p, can we get exactly p? Subsequence gcd must divide g. If g != p,
// # impossible to hit exactly p as gcd of a subsequence of multiples. So we need g == p
// # for any hope.
// #
// # Length < n
// # Let cnt = count of indices with nums[i] % p == 0.
// # Case A) cnt < n: there is at least one index not divisible by p. Then the subsequence
// #   formed by taking ALL cnt multiples of p has length cnt < n and gcd = g. If g == p,
// #   this is a good subsequence. So g==p is sufficient.
// # Case B) cnt == n: every entry is a multiple of p, so any subsequence that includes
// #   "all positions" has length n, which is NOT allowed. We must EXCLUDE at least one
// #   index. The question becomes: is there an index i such that gcd of the other n-1
// #   stored values is still p?
// #   - If n > 6: a combinatorial number-theory fact (used in official solutions) shows
// #     that whenever the full-array gcd among multiples is p, such a deletion always
// #     exists. So we only need g == p.
// #   - If n <= 6: brute-force which index to drop: for each i, compute gcd of
// #     prefix [1..i-1] and suffix [i+1..n] on the stored array (zeros for non-multiples,
// #     but here all are multiples). If some split gives gcd p, good.
// #
// # Why segment tree
// # - Point updates from queries: O(log n) each.
// # - Range GCD queries for the n<=6 check: O(log n) per trial, at most 6 trials -> tiny.
// # - Total across q queries: O((n + q) log n).
// #
// # Alternatives (why not simpler DS)
// # - Naive full gcd recompute each query: O(n q) -> too slow for n,q up to 5e4.
// # - Fenwick tree does not naturally compose gcd over intervals the same way (gcd is not
// #   invertible like sum); segment tree is standard.
// #
// # Time complexity
// # Build O(n); each query: O(log n) updates + maybe O(n * log n) when n<=6 for at most 6
// # positions -> O(log n) amortized per query for large n. Overall O((n + q) log n).
// #
// # Space complexity
// # O(n) for the segment tree (~4n nodes with gcd ints).
// #
// # Edge cases
// # - cnt == 0: all zeros in tree -> root g = 0 != p (unless p==0, but p>=1) -> fail.
// # - p divides everything and gcd == p but n==2 and need delete one: brute handles.
// # - Repeated updates same index: logic removes old contribution then adds new (both mod p).
// #
// # Tests (match examples)
// # Example 1: [4,8,12,16], p=2 -> after second update gcd of multiples {8,6,16}=2, cnt=3<4.
// # Example 2: p=3 two successes after updates.
// # Example 3: no multiple-of-2 configuration yields gcd 2 as needed with length rule.
// #
// # Interview explanation order
// # 1) Reduce to multiples of p; others only shrink feasible length without changing gcd
// #    of the "multiples-only" part.
// # 2) Track global gcd g of multiples via segment tree point updates.
// # 3) If g != p -> impossible.
// # 4) If cnt < n -> take all multiples (length cnt), done when g==p.
// # 5) If cnt == n -> need drop one index; use theorem for n>6 else brute 6 tries with
// #    range gcd queries.
// # --- end notes ---
// 
// # @lc code=start
// from math import gcd
// 
// 
// class Node:
//     __slots__ = "l", "r", "g"
// 
//     def __init__(self, l: int, r: int):
//         self.l = l
//         self.r = r
//         self.g = 0
// 
// 
// class SegmentTree:
//     __slots__ = "tr"
// 
//     def __init__(self, n: int):
//         self.tr: list[Node | None] = [None] * (n << 2)
//         self.build(1, 1, n)
// 
//     def build(self, u: int, l: int, r: int):
//         self.tr[u] = Node(l, r)
//         if l == r:
//             return
//         mid = (l + r) >> 1
//         self.build(u << 1, l, mid)
//         self.build(u << 1 | 1, mid + 1, r)
// 
//     def pushup(self, u: int):
//         self.tr[u].g = gcd(self.tr[u << 1].g, self.tr[u << 1 | 1].g)
// 
//     def modify(self, u: int, x: int, v: int):
//         if self.tr[u].l == self.tr[u].r:
//             self.tr[u].g = v
//             return
//         mid = (self.tr[u].l + self.tr[u].r) >> 1
//         if x <= mid:
//             self.modify(u << 1, x, v)
//         else:
//             self.modify(u << 1 | 1, x, v)
//         self.pushup(u)
// 
//     def query(self, u: int, l: int, r: int) -> int:
//         if l > r:
//             return 0
//         if self.tr[u].l >= l and self.tr[u].r <= r:
//             return self.tr[u].g
//         mid = (self.tr[u].l + self.tr[u].r) >> 1
//         if r <= mid:
//             return self.query(u << 1, l, r)
//         if l > mid:
//             return self.query(u << 1 | 1, l, r)
//         return gcd(self.query(u << 1, l, mid), self.query(u << 1 | 1, mid + 1, r))
// 
// 
// class Solution:
//     def countGoodSubseq(self, nums: list[int], p: int, queries: list[list[int]]) -> int:
//         n = len(nums)
//         tree = SegmentTree(n)
//         cnt = 0
// 
//         for i, x in enumerate(nums, 1):
//             if x % p == 0:
//                 tree.modify(1, i, x)
//                 cnt += 1
// 
//         ans = 0
//         for idx, val in queries:
//             if nums[idx] % p == 0:
//                 tree.modify(1, idx + 1, 0)
//                 cnt -= 1
//             if val % p == 0:
//                 tree.modify(1, idx + 1, val)
//                 cnt += 1
//             nums[idx] = val
// 
//             if tree.tr[1].g != p:
//                 continue
// 
//             if cnt < n or n > 6:
//                 ans += 1
//                 continue
// 
//             for i in range(1, n + 1):
//                 left_g = tree.query(1, 1, i - 1)
//                 right_g = tree.query(1, i + 1, n)
//                 if gcd(left_g, right_g) == p:
//                     ans += 1
//                     break
// 
//         return ans
// 
// 
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

struct Node {
    int l, r, g;
};

class SegmentTree {
public:
    vector<Node> tr;
    SegmentTree(int n) : tr(n << 2) { build(1, 1, n); }
    void build(int u, int l, int r) {
        tr[u] = {l, r, 0};
        if (l == r) return;
        int m = (l + r) >> 1;
        build(u << 1, l, m);
        build(u << 1 | 1, m + 1, r);
    }
    void pushup(int u) { tr[u].g = std::gcd(tr[u << 1].g, tr[u << 1 | 1].g); }
    void modify(int u, int x, int v) {
        if (tr[u].l == tr[u].r) {
            tr[u].g = v;
            return;
        }
        int m = (tr[u].l + tr[u].r) >> 1;
        if (x <= m) modify(u << 1, x, v);
        else modify(u << 1 | 1, x, v);
        pushup(u);
    }
    int query(int u, int l, int r) {
        if (l > r) return 0;
        if (l <= tr[u].l && tr[u].r <= r) return tr[u].g;
        int m = (tr[u].l + tr[u].r) >> 1;
        if (r <= m) return query(u << 1, l, r);
        if (l > m) return query(u << 1 | 1, l, r);
        return std::gcd(query(u << 1, l, m), query(u << 1 | 1, m + 1, r));
    }
};

class Solution {
public:
    int countGoodSubseq(vector<int>& nums, int p, vector<vector<int>>& queries) {
        int n = nums.size();
        SegmentTree tree(n);
        int cnt = 0;
        for (int i = 0; i < n; ++i) if (nums[i] % p == 0) {
            tree.modify(1, i + 1, nums[i]);
            ++cnt;
        }
        int ans = 0;
        for (auto& q : queries) {
            int idx = q[0], val = q[1];
            if (nums[idx] % p == 0) {
                tree.modify(1, idx + 1, 0);
                --cnt;
            }
            if (val % p == 0) {
                tree.modify(1, idx + 1, val);
                ++cnt;
            }
            nums[idx] = val;
            if (tree.tr[1].g != p) continue;
            if (cnt < n || n > 6) {
                ++ans;
                continue;
            }
            for (int i = 1; i <= n; ++i) {
                if (std::gcd(tree.query(1, 1, i - 1), tree.query(1, i + 1, n)) == p) {
                    ++ans;
                    break;
                }
            }
        }
        return ans;
    }
};
