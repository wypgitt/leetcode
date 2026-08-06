/*
 * @lc app=leetcode id=260 lang=cpp
 *
 * [260] Single Number III
 */
// Translated from 260.single-number-iii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=260 lang=python3
// #
// # [260] Single Number III
// #
// # =============================================================================
// # PROBLEM (precise)
// # =============================================================================
// #
// # Every integer in nums appears **exactly twice**, except **two distinct integers**
// # that appear **exactly once**. Return those two singletons (order arbitrary unless
// # the judge fixes it).
// #
// # =============================================================================
// # WHY XOR (algorithm choice)
// # =============================================================================
// #
// # **Pairs cancel:** For any x, **x XOR x = 0**. So if we XOR **all** elements,
// # every duplicated value vanishes and we’re left with **a XOR b**, where **a** and
// # **b** are the two unique numbers we want.
// #
// # We **cannot** recover a and b from **a XOR b** alone — information is missing — but
// # we can **split** the array using one distinguishing bit between **a** and **b**.
// #
// # Let **s = a XOR b**. Since **a ≠ b**, **s ≠ 0**, so **s** has at least one bit set.
// # Pick **any** such bit (common trick: the **lowest** set bit **lowbit(s) = s & -s**
// # in two’s-complement arithmetic). Then **a** and **b** differ on that bit — one has
// # it 0, the other 1.
// #
// # **Partition** nums into two groups: numbers whose bit is 0 vs 1 at that position.
// # - Duplicated numbers **always land in the same group together**, so they still
// #   cancel within each group when XOR-reduced.
// # - The two singletons land in **different** groups, so each group’s XOR reduces to
// #   exactly **one** of **{a, b}**.
// #
// # Two linear passes: **O(n)** time, **O(1)** extra space (only integers / two XOR
// # accumulators). No hash map needed — though a frequency map also works in **O(n)**
// # time but **O(n)** space; XOR is the canonical “interview elegant” answer.
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # - **Scalars only:** running XOR **s**, bitmask **diff**, two XOR buckets **x** and
// #   **y** (or reuse pattern with two accumulators). **No** auxiliary arrays sized by
// #   **n** — **O(1)** extra space beyond the input list reference.
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY (analysis)
// # =============================================================================
// #
// # **Time:** Two passes over **nums** → **O(n)**.
// # **Space:** Constant extra integers → **O(1)** (output list of length 2 does not
// # dominate asymptotics).
// #
// # Compare: sorting **O(n log n)**; HashMap counts **O(n)** time and **O(n)** space.
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # - **Exactly two distinct singletons** guaranteed when input valid — smallest size is
// #   often **4** elements (two pairs + pattern varies); problem guarantees existence.
// # - **Negative numbers:** XOR / bit tests behave consistently on two’s-complement
// #   representations in Python’s arbitrary-precision ints — **lowbit** trick still valid.
// # - **Return order:** problem typically accepts either order; sorting the pair is a
// #   harmless normalization for debugging / deterministic tests.
// #
// # =============================================================================
// # TESTING
// # =============================================================================
// #
// # - Known example(s) from statement.
// # - Random stress: build multiset with pairs + two distinct values; XOR solution vs
// #   Counter-reference on many seeds.
// # - Edge: range of ints including negatives.
// #
// # =============================================================================
// # POSSIBLE VARIANTS / IMPROVEMENTS
// # =============================================================================
// #
// # - Choose **any** set bit of **s** (not only lowbit), e.g. iterate bit index — same
// #   asymptotics, slightly more code.
// # - If overflow were an issue (not in Python), still XOR in fixed-width **unsigned**
// #   interpretation for the bit test.
// #
// # =============================================================================
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def singleNumber(self, nums: List[int]) -> List[int]:
//         """
//         Return the two integers that appear exactly once; all others appear twice.
// 
//         XOR everything to get a^b; isolate a differing bit; split nums by that bit and
//         XOR each half to recover the two values.
//         """
//         xor_ab = 0
//         for x in nums:
//             xor_ab ^= x
// 
//         # Lowest set bit of (a ^ b): a and b differ here; pairs share fate per group.
//         diff_bit = xor_ab & (-xor_ab)
// 
//         a = b = 0
//         for x in nums:
//             if x & diff_bit:
//                 a ^= x
//             else:
//                 b ^= x
// 
//         return sorted([a, b])
// 
// 
// # lc-original code=end

// @lc code=start
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
    vector<int> singleNumber(vector<int>& nums) {
        int xab = 0;
        for (int x : nums) xab ^= x;
        int bit = xab & -xab;
        int a = 0, b = 0;
        for (int x : nums) {
            if (x & bit) a ^= x;
            else b ^= x;
        }
        vector<int> ans{a, b};
        sort(ans.begin(), ans.end());
        return ans;
    }
};
// @lc code=end
