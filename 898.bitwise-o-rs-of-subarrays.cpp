// Translated from 898.bitwise-o-rs-of-subarrays.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=898 lang=python3
// #
// # [898] Bitwise ORs of Subarrays
// #
// 
// # =============================================================================
// # INTERVIEW: ELEVATOR PITCH (~30 seconds)
// # =============================================================================
// #
// # "We need distinct values of (subarray OR) over all contiguous subarrays. Naively
// # that’s O(n³) — enumerate ends, starts, and OR the segment. OR only ever **sets**
// # bits, never clears them, so for a **fixed right endpoint** there are only O(B)
// # different OR results as the left border slides (B ≤ bit-width). Carry a small set
// # ‘current ORs ending here’, update in O(size of set) per element, merge into a
// # global distinct set — **O(n · B)** time, **O(answer)** space."
// #
// # =============================================================================
// # PROBLEM (PRECISE)
// # =============================================================================
// #
// # Given integer array `arr`, consider every **non-empty** contiguous subarray
// # `arr[i:j+1]`. Compute the bitwise **OR** of each subarray’s elements. Return how
// # **many distinct** integers appear among those OR results.
// #
// # =============================================================================
// # WHY NAIVE ENUMERATION FAILS
// # =============================================================================
// #
// # • **O(n²)** subarrays; each OR across length L costs **O(L)** if done naively → **O(n³)**
// #   total — too slow for **n ≈ 10⁵**.
// # • We only need **distinctness**, not multiplicity — suggests **incremental merging**
// #   of candidate values rather than full scans.
// #
// # =============================================================================
// # KEY OBSERVATION — OR IS MONOTONE IN THE LEFT BORDER
// # =============================================================================
// #
// # Fix the **right** endpoint at index `r`. Let
// #
// #       F(r, i) = arr[i] | arr[i+1] | … | arr[r]   for i ≤ r.
// #
// # As **`i` decreases** (subarray lengthens leftward), `F(r, i)` can only **gain** bits
// # OR-ing in more numbers — in terms of the integer value, it is **non-decreasing**
// # in the bitwise sense (superset of set bits). Therefore as `i` walks left, `F(r,i)`
// # changes only when **new bits flip on** — at most **B** times for **B**-bit integers
// # (e.g. **≤ 32** for 32-bit inputs).
// #
// # So for each `r`, the set **`{ F(r,i) : i = 0…r }`** has **O(B)** distinct values,
// # not **O(r)**.
// #
// # =============================================================================
// # ALGORITHM — INCREMENTAL SET `cur`
// # =============================================================================
// #
// # Maintain **`cur`** = set of all OR values of subarrays **ending at the previous**
// # index (after processing `arr[r-1]`). When `arr[r]` arrives:
// #
// #   • Every old subarray ending at `r−1` extends by OR-ing `arr[r]` → value `y | x`
// #     for each `y` in `cur`.
// #   • The subarray consisting **only** of `arr[r]` contributes OR `x`.
// #
// # Update:
// #
// #       cur ← { x } ∪ { y | x for all y in old_cur }
// #
// # Union **all** `cur` into a global distinct set `ans`, then report **`len(ans)`**.
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # • **`set` (hash set)** — deduplicates OR values automatically; **O(1)** average
// #   insert / membership for integers.
// # • **`cur`** holds **O(B)** integers per step in theory — small constant for fixed
// #   bit-width.
// #
// # Alternatives: compact **sorted list** + dedupe (same asymptotics); **bitset** only
// # if value universe tiny — here values can be large, so store explicit ints.
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY
// # =============================================================================
// #
// # Let **B** = number of bits in values (≤ **31** for LeetCode’s signed 32-bit inputs).
// #
// # • Each step: build new `cur` from old `cur` of size **O(B)** → **O(B)** work.
// # • **n** steps → **O(n · B)** time; with **B** constant, **O(n)** in the typical
// #   competitive-programming sense.
// # • **Space:** **`ans`** stores every distinct OR ever seen — **O(|output|)** ≤ **O(n·B)**
// #   worst case; **`cur`** is **O(B)** auxiliary per layer.
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # • **`n == 1`** — answer **1** (single OR = `arr[0]`).
// # • **Repeated values** — `cur` and `ans` are sets; duplicates collapse.
// # • **Zeros** — `0 | x = x`; sets still correct.
// #
// # =============================================================================
// # TESTING (UNIT / REGRESSION)
// # =============================================================================
// #
// # • `[1,2,4]` → OR results `{1,2,3,4,6,7}` → **6** distinct (match hand enumeration).
// # • `[0]` → **1**.
// # • Brute force **O(n²)** over small random arrays (bitwise OR with accumulate) vs
// #   optimized counter — must agree.
// #
// # =============================================================================
// # IMPROVEMENTS / VARIANTS
// # =============================================================================
// #
// # • **List + manual dedupe** if set overhead matters (micro-optimization).
// # • **Two-pointer on sorted unique chain** — possible but set solution is standard.
// #
// # =============================================================================
// 
// # @lc code=start
// from typing import List, Set
// 
// 
// class Solution:
//     def subarrayBitwiseORs(self, arr: List[int]) -> int:
//         """
//         Count distinct bitwise-OR results over all non-empty contiguous subarrays.
// 
//         For each new element x, new ORs ending here are x alone and (old_or | x)
//         for every old_or that ended at the previous index. Union into answer set.
//         """
//         ans: Set[int] = set()
//         cur: Set[int] = set()
// 
//         for x in arr:
//             cur = {x} | {y | x for y in cur}
//             ans.update(cur)
// 
//         return len(ans)
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

class Solution {
public:
    int subarrayBitwiseORs(vector<int>& arr) {
        unordered_set<int> ans, cur;
        for (int x : arr) {
            unordered_set<int> nxt{x};
            for (int y : cur) nxt.insert(y | x);
            cur.swap(nxt);
            ans.insert(cur.begin(), cur.end());
        }
        return ans.size();
    }
};
