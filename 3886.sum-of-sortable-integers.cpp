// Translated from 3886.sum-of-sortable-integers.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3886 lang=python3
// #
// # [3886] Sum of Sortable Integers
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
// # @lc app=leetcode id=3886 lang=python3
// #
// # [3886] Sum of Sortable Integers
// #
// # --- Notes (problem restatement, characterization, algorithm, complexity, interview) ---
// #
// # Problem restatement
// # nums length n. Integer k (positive divisor of n) is SORTABLE iff we can reach the fully
// # NON-DECREASING arrangement of nums by:
// #   1) Split nums into consecutive blocks of length k (exactly n/k blocks).
// #   2) Inside EACH block, apply cyclic rotations (left/right any number of times) —
// #      only orders reachable from the original block order are cyclic shifts.
// # Sum EVERY divisor k of n for which k is sortable; return that sum.
// #
// # Characterization of sortability for fixed k
// # Let S = sorted(nums) (global target order). For concatenated blocks to equal S, block i
// # (0-indexed) MUST realize exactly S[i*k : (i+1)*k] as values in order — those are the k
// # multiset positions in the sorted array for that segment.
// # So for each block:
// #   (a) Multiset(block_i from nums) = multiset(S[i*k : (i+1)*k]).
// #   (b) The physical block in nums must be a CYCLIC ROTATION of the target segment S[i*k:(i+1)*k]
// #       as sequences (same length, same multiset, one is a rotate of the other).
// # If (a) fails, wrong multiset — impossible. If (a) holds but (b) fails, we cannot rotate the
// # original trace into the sorted segment order — impossible.
// # If both hold for every block, k is sortable.
// #
// # Special cases
// # - k = n: one block; sortable iff nums is a cyclic rotation of sorted(nums) — e.g. [3,1,2]
// #   works because it rotates to [1,2,3].
// # - k = 1: each block is one element; rotation does nothing. Sortable iff nums is ALREADY
// #   sorted (each position must match S).
// # - nums already sorted: every divisor k works (use identity rotation per block) — Example 3.
// #
// # Checking cyclic rotation in O(k) — important for performance
// # Compare multisets (Counter or sorted(block) vs seg). Segment seg = S[i:i+k] is already
// # non-decreasing, so multiset equality is Counter(block)==Counter(seg) in O(k), or
// # sorted(block)==seg without sorting seg.
// # Rotation: block must occur as a length-k window in (seg + seg). A naive scan over k start
// # offsets with full slice compare is O(k^2) per block and TIME LIMITS on large n (e.g. k ~ n/2).
// # Use KMP substring search on integer arrays: O(k) per block.
// #
// # Why enumerate divisors of n
// # k must divide n so that integer-length blocks tile the array; only those k are candidates.
// #
// # Algorithm
// #   S = sorted(nums)
// #   ans = 0
// #   for each divisor k of n:
// #       if all blocks pass multiset + rotation checks: ans += k
// #   return ans
// #
// # Time complexity
// # Let tau(n) be the number of divisors of n (for n <= 1e5, tau(n) is small, ~128 worst-ish).
// # For each divisor, sum over blocks of O(k) multiset + O(k) KMP = O(n) per divisor.
// # Overall O(n * tau(n)); avoid O(k^2) rotation naive scan.
// #
// # Space complexity
// # O(n) for sorted copy and temporary doubled segment seg+seg (length 2k per block worst O(n)
// # for single block).
// #
// # Possible improvements
// # - Double rolling hash instead of KMP (same O(k); watch collisions).
// # - For multiset only, sorted(block)==seg when seg is sorted — still O(k log k); Counter is O(k).
// #
// # Edge cases
// # - All equal values: any rotation works; sorted equals nums pattern — typically all k pass if
// #   multisets align per block (they will).
// # - n prime: divisors 1 and n only.
// #
// # Interview walkthrough
// # 1) Observe global sorted target S fixes each block's multiset and order segment S[i*k:...].
// # 2) Independent cyclic rotations per block -> each block must be a rotation of that segment.
// # 3) Implement divisor enumeration + O(n) validation per k.
// # 4) Argue O(n * tau(n)) time.
// # --- end notes ---
// 
// # @lc code=start
// from collections import Counter
// 
// 
// class Solution:
//     def sortableIntegers(self, nums: list[int]) -> int:
//         n = len(nums)
//         s = sorted(nums)
// 
//         def kmp_contains(pat: list[int], txt: list[int]) -> bool:
//             """Return True iff pat occurs as a contiguous subarray of txt (KMP)."""
//             if not pat:
//                 return True
//             m, ln = len(pat), len(txt)
//             if m > ln:
//                 return False
//             lps = [0] * m
//             length = 0
//             i = 1
//             while i < m:
//                 if pat[i] == pat[length]:
//                     length += 1
//                     lps[i] = length
//                     i += 1
//                 else:
//                     if length > 0:
//                         length = lps[length - 1]
//                     else:
//                         lps[i] = 0
//                         i += 1
//             j = 0
//             i = 0
//             while i < ln:
//                 if txt[i] == pat[j]:
//                     i += 1
//                     j += 1
//                     if j == m:
//                         return True
//                 elif j > 0:
//                     j = lps[j - 1]
//                 else:
//                     i += 1
//             return False
// 
//         def divisors(x: int):
//             i = 1
//             while i * i <= x:
//                 if x % i == 0:
//                     yield i
//                     if i * i != x:
//                         yield x // i
//                 i += 1
// 
//         def ok(k: int) -> bool:
//             for i in range(0, n, k):
//                 block = nums[i : i + k]
//                 seg = s[i : i + k]
//                 if Counter(block) != Counter(seg):
//                     return False
//                 if not kmp_contains(block, seg + seg):
//                     return False
//             return True
// 
//         return sum(d for d in divisors(n) if ok(d))
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
    bool kmpContains(const vector<int>& pat, const vector<int>& txt) {
        if (pat.empty()) return true;
        if (pat.size() > txt.size()) return false;
        int m = pat.size();
        vector<int> lps(m);
        for (int i = 1, len = 0; i < m;) {
            if (pat[i] == pat[len]) lps[i++] = ++len;
            else if (len) len = lps[len - 1];
            else lps[i++] = 0;
        }
        for (int i = 0, j = 0; i < (int)txt.size();) {
            if (txt[i] == pat[j]) {
                ++i;
                if (++j == m) return true;
            } else if (j) j = lps[j - 1];
            else ++i;
        }
        return false;
    }

    vector<int> divisors(int x) {
        vector<int> out;
        for (int i = 1; i * i <= x; ++i) if (x % i == 0) {
            out.push_back(i);
            if (i * i != x) out.push_back(x / i);
        }
        return out;
    }

public:
    int sortableIntegers(vector<int>& nums) {
        int n = nums.size();
        vector<int> sorted = nums;
        sort(sorted.begin(), sorted.end());
        auto ok = [&](int k) {
            for (int i = 0; i < n; i += k) {
                vector<int> block(nums.begin() + i, nums.begin() + i + k);
                vector<int> seg(sorted.begin() + i, sorted.begin() + i + k);
                auto a = block, b = seg;
                sort(a.begin(), a.end());
                sort(b.begin(), b.end());
                if (a != b) return false;
                vector<int> doubled = seg;
                doubled.insert(doubled.end(), seg.begin(), seg.end());
                if (!kmpContains(block, doubled)) return false;
            }
            return true;
        };
        int ans = 0;
        for (int d : divisors(n)) if (ok(d)) ans += d;
        return ans;
    }
};
