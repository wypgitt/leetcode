/*
 * @lc app=leetcode id=2663 lang=cpp
 *
 * [2663] Lexicographically Smallest Beautiful String
 */
// Translated from 2663.lexicographically-smallest-beautiful-string.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=2663 lang=python3
// #
// # [2663] Lexicographically Smallest Beautiful String
// #
// 
// # --- Interview notes (definition, observations, algorithm, complexity, tests, edges) ---
// #
// # Problem (summary)
// # Alphabet is the first k lowercase letters: 'a' .. chr(ord('a') + k - 1).
// # A string is beautiful iff it has NO palindrome of length 2 or 3 as a contiguous substring.
// # Given a beautiful string s and integer k, return the lexicographically smallest beautiful string
// # that is STRICTLY LARGER than s (same length). If none exists, return "".
// #
// # Equivalent local constraints (why this is O(1) check per position)
// # - Length-2 palindrome "aa" ⟺ two equal adjacent characters ⟺ s[i] == s[i-1].
// # - Length-3 palindrome "aba" ⟺ ends match around middle ⟺ s[i] == s[i-2].
// # So beautiful ⇔ for all valid i: s[i] ≠ s[i-1] and s[i] ≠ s[i-2].
// # (Longer palindromes are irrelevant to the definition.)
// #
// # Why greedy “next string” from the right works
// # Lexicographic order is like base-(k) counting on fixed length n: to get the smallest string > s,
// # take the rightmost position where we can increase a digit (letter), increase it by the minimum
// # amount allowed, then fill everything to the right with the smallest legal suffix.
// # Uniqueness: any string larger than s either differs at the same rightmost bump position (and our
// # bump is minimal valid) or differs further left (strictly larger lex bump), so right-to-left first
// # success yields the global minimum > s.
// #
// # Algorithm
// # 1. Convert to mutable list for in-place edits.
// # 2. For i from n-1 down to 0 (try to bump as far right as possible):
// #    For letter index j from (current letter + 1) .. k-1:
// #      Let c = chr('a' + j). Skip if c equals left neighbor (pal length 2) or second-left (pal len 3).
// #      Assign s[i] = c.
// #      Greedy-fill positions p = i+1 .. n-1: at each p pick smallest letter in 0..k-1 that passes
// #      the same two checks against already-fixed s[p-1] and s[p-2].
// #      If some p has no valid letter, abort this bump try (continue to next j or previous i).
// #      If fill succeeds, return the joined string.
// # 3. If no bump works, return "".
// #
// # Data structures
// # - List of chars: O(n) mutable prefix/suffix construction; no stack or DP needed.
// # - Alphabet size k is small (typically ≤ 26), so scanning letters 0..k-1 per position is constant per k.
// #
// # Time complexity
// # - Outer i: O(n). Middle j: O(k). Inner fill: O((n - i) * k) in worst case.
// # - Worst-case upper bound O(n^2 * k) (or O(n^2 * k^2) if counted naïvely); with typical constraints
// #   (small k, moderate n) this passes easily.
// #
// # Space complexity
// # O(n) for the mutable copy of s (output-sized).
// #
// # Edge cases (talk through in interview)
// # - n == 1: only need smallest letter > s[0]; if s[0] is already max letter for alphabet, return "".
// # - k == 2: alphabet {a,b}; beautiful strings alternate ... often tight; many bumps impossible → "".
// # - Input guaranteed beautiful in statement — we never validate s; our construction preserves beauty.
// #
// # Tests (manual / mental)
// # - smallestBeautifulString("abcz", 26) → bump 'c'→'d', suffix smallest → "abda".
// # - smallestBeautifulString("dc", 4) → cannot exceed without breaking beauty → "".
// # - smallestBeautifulString("a", 10) → "b".
// # Optional property check: if result r non-empty, assert r > s and `is_beautiful(r)` with the two rules.
// #
// # Improvements
// # - For huge n one might micro-optimize fill with bitmasks of forbidden {prev, prev2} letters (O(1)
// #   choice among ≤3 blocked letters when k=26), but interview solution rarely requires it.
// #
// # Python implementation detail (easy to break while refactoring)
// # - `for p ... else: return` attaches `else` to `for p`: it runs iff the `for p` loop did not execute
// #   `break` (the `break` lives in the `for t` clause when no letter fits position p).
// # - If `range(i + 1, n)` is empty (suffix length 0), `for p` runs zero iterations and `else` still
// #   runs — correct: after bumping the last character, return immediately.
// #
// # --- end notes ---
// 
// # lc-original code=start
// class Solution:
//     def smallestBeautifulString(self, s: str, k: int) -> str:
//         s = list(s)
//         n = len(s)
//         for i in range(n - 1, -1, -1):
//             for j in range(ord(s[i]) - ord("a") + 1, k):
//                 c = chr(ord("a") + j)
//                 if i > 0 and c == s[i - 1]:
//                     continue
//                 if i > 1 and c == s[i - 2]:
//                     continue
//                 s[i] = c
//                 for p in range(i + 1, n):
//                     for t in range(k):
//                         d = chr(ord("a") + t)
//                         if p > 0 and d == s[p - 1]:
//                             continue
//                         if p > 1 and d == s[p - 2]:
//                             continue
//                         s[p] = d
//                         break
//                     else:
//                         break
//                 else:
//                     return "".join(s)
//         return ""
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
    string smallestBeautifulString(string s, int k) {
        int n = s.size();
        for (int i = n - 1; i >= 0; --i) {
            for (int j = s[i] - 'a' + 1; j < k; ++j) {
                char c = char('a' + j);
                if (i > 0 && c == s[i - 1]) continue;
                if (i > 1 && c == s[i - 2]) continue;
                s[i] = c;
                bool ok = true;
                for (int p = i + 1; p < n && ok; ++p) {
                    ok = false;
                    for (int t = 0; t < k; ++t) {
                        char d = char('a' + t);
                        if (p > 0 && d == s[p - 1]) continue;
                        if (p > 1 && d == s[p - 2]) continue;
                        s[p] = d;
                        ok = true;
                        break;
                    }
                }
                if (ok) return s;
            }
        }
        return "";
    }
};
// @lc code=end
