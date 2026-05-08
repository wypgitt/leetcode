// Translated from 1163.last-substring-in-lexicographical-order.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1163 lang=python3
// #
// # [1163] Last Substring In Lexicographical Order
// #
// 
// # --- Interview notes (reduce to max suffix, two-pointer duel, complexity, edges, alternatives) ---
// #
// # Problem
// # Among all contiguous substrings of `s`, return the lexicographically largest one (string comparison in dictionary order).
// #
// # Key reduction — optimal substring always ends at the last character
// # Suppose an optimal substring is s[l : r+1] with r < n - 1. Compare it with s[l : r+2] (one character longer on the
// # right). They agree on the first (r - l + 1) characters; at the next position the longer substring has a concrete
// # character while the shorter has “nothing” — so the longer is lexicographically larger. Hence any non-maximal-right-end
// # substring can be strictly improved by extending to index n - 1.
// # Therefore the answer is always s[i:] for some starting index i ∈ [0, n - 1] — i.e. **some suffix of s**.
// #
// # Reformulation
// # Find the suffix of `s` that is lexicographically maximum among all n suffixes.
// #
// # Naive approach
// # Compare every pair of suffixes — O(n²) character comparisons worst-case; too slow for |s| up to 4·10⁵ (LeetCode).
// #
// # Chosen approach — O(n) two-pointer “suffix duel” (Booth–Duval style idea)
// # Maintain index `i` = current best candidate for where the maximum suffix starts, and `j` = challenger start (`j > i`).
// # Compare characters with offset `k`: s[i+k] vs s[j+k].
// # • Equal → increase k (common prefix of the two suffixes grows).
// # • s[i+k] < s[j+k] → suffix starting at `i` loses to suffix starting at `j` at the first differing position. Any start
// #   index in [i, i+k] also loses to `j` (those suffixes share the bad prefix relative to j). Jump `i` past that block:
// #   `i ← max(i + k + 1, j)` so we never revisit discarded positions; reset `k`, and set `j ← i + 1` as the next challenger.
// # • s[i+k] > s[j+k] → challenger loses; advance `j` past the mismatched block: `j ← j + k + 1`, reset `k`.
// # Loop while `j + k < n` (room for challenger suffix). Return `s[i:]`.
// #
// # Why `i ← max(i + k + 1, j)`?
// # After proving suffix at `i` is worse than suffix at `j`, starts strictly between `i` and `j` can also be eliminated or
// # must stay consistent with ordering — the `max` avoids moving `i` backward when `j` had already passed `i+k+1`.
// #
// # Time complexity
// # Each failed comparison advances either `i` or `j` by at least one; pointer moves sum to O(n); `k` resets but total work
// # is linear — **O(n)** character comparisons amortized.
// #
// # Space complexity
// # **O(1)** extra (only indices); output substring shares underlying storage view in theory (Python slice copies — problem
// # treats return as conceptual).
// #
// # Edge cases
// # • |s| = 1 → answer is `s`.
// # • All characters equal → every suffix begins with the same run; algorithm returns **whole string** `s` (maximum suffix
// #   is s[0:]).
// #
// # Tests (sanity / statement-style)
// # • "leetcode" → "tcode"
// # • "abab" → "bab"
// # • "a" → "a"
// # • "aaa" → "aaa"
// #
// # Alternative algorithms (trade-offs)
// # • **Suffix array + LCP** in O(n log n) or O(n) — overkill here but generalizes to many suffix queries.
// # • **Rolling hash + binary search** per pair — still slower than linear two-pointer for single max suffix.
// # • **Naive** compare all suffix pairs — O(n²), simple but fails constraints.
// #
// # Improvements
// # • Implementation uses only integer indices — cache-friendly, no auxiliary arrays.
// # • For interviews, prove “answer is a suffix ending at n−1” first, then present two-pointer duel as linear-time max suffix.
// #
// # --- end notes ---
// 
// # @lc code=start
// class Solution:
//     def lastSubstring(self, s: str) -> str:
//         i, j, k, n = 0, 1, 0, len(s)
//         while j + k < n:
//             if s[i + k] == s[j + k]:
//                 k += 1
//             elif s[i + k] < s[j + k]:
//                 i = max(i + k + 1, j)
//                 k = 0
//                 j = i + 1
//             else:
//                 j += k + 1
//                 k = 0
//         return s[i:]
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
    string lastSubstring(string s) {
        int i = 0, j = 1, k = 0, n = s.size();
        while (j + k < n) {
            if (s[i + k] == s[j + k]) ++k;
            else if (s[i + k] < s[j + k]) {
                i = max(i + k + 1, j);
                k = 0;
                j = i + 1;
            } else {
                j += k + 1;
                k = 0;
            }
        }
        return s.substr(i);
    }
};
