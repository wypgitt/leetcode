/*
 * @lc app=leetcode id=2584 lang=cpp
 *
 * [2584] Split the Array to Make Coprime Products
 */
// Translated from 2584.split-the-array-to-make-coprime-products.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=2584 lang=python3
// #
// # [2584] Split the Array to Make Coprime Products
// #
// # --- Notes (problem, math, algorithm, DS, complexity, tests, edges, improvements, interview) ---
// #
// # Problem restatement
// # Given nums (length n), find the smallest index i with 0 <= i <= n - 2 such that
// #   gcd( nums[0] * ... * nums[i],  nums[i+1] * ... * nums[n-1] ) == 1.
// # If none exists, return -1.
// # Equivalently: split into two non-empty contiguous parts whose PRODUCTS are coprime.
// #
// # Number theory reduction
// # gcd(A, B) > 1 iff some prime p divides both A and B.
// # The product of a subarray is divisible by p iff at least one element in that subarray is
// # divisible by p. So the split after i is VALID iff no prime p divides an element on BOTH sides
// # of the split — i.e. there is no prime whose occurrences straddle the boundary between i and i+1.
// #
// # Why not multiply huge products?
// # nums can be large; products overflow and are unnecessary. Only prime presence matters.
// #
// # Algorithm (two-pointer / sweep with frequency counts)
// # Pre-count, for each prime p, how many ARRAY POSITIONS (elements) to the RIGHT of the scan will
// # still contain p after we remove indices — implemented as a multiset counter over positions:
// #   - Build rightPrimeFactors: for each nums[k], for each distinct prime p | nums[k], increment
// #     rightPrimeFactors[p] (number of not-yet-processed indices on the right that still owe p).
// # Actually the editorial counts: total occurrences-weighted by elements — each index contributes
// # once per distinct prime dividing nums[i].
// #
// # Sweep i = 0 .. n-2:
// #   Move nums[i] from "right side" to "left side" conceptually:
// #   For each distinct prime p in nums[i]:
// #     Decrement rightPrimeFactors[p].
// #     If it becomes 0: p no longer appears strictly to the right of i — remove p from both counters
// #       (nothing left on right; no "spanning" concern for p).
// #     Else: p still appears somewhere to the right of i, AND already appears in nums[0..i], so p
// #       spans the split after i — record that by incrementing leftPrimeFactors[p] (or equivalent).
// #   After updating, if leftPrimeFactors is empty, NO prime spans both sides -> split after i works.
// # Return the first such i (scan order is increasing i -> smallest valid split).
// #
// # Correctness sketch
// # After processing index i, leftPrimeFactors[p] > 0 iff p divides some element in nums[0..i] AND
// # some element in nums[i+1..n-1]. That is exactly "p bridges the boundary". Empty map <=> no such p.
// #
// # Data structures
// # - collections.Counter (or two dicts) for right-side multiplicities and "bridging" primes.
// # - Unique prime factors per nums[i] from trial division / sieve — list of ints per element.
// # - When right[p] hits 0, use left_bridge.pop(p, None): p may only exist on the left now and never
// #   entered left_bridge (safe across Python versions).
// #
// # Prime factorization helper
// # For nums[i] <= 10^6 (typical constraint), trial divide up to min(1000, num): any composite <= 10^6
// # has a factor <= 1000. After stripping small factors, what remains is 1 or a prime > 1000 (append).
// # Edge: nums[i] == 1 has no prime factors — contributes nothing to counters.
// #
// # Time complexity
// # - Building right counts: O(n * F) where F is number of trial divisions per value (~sqrt(V) worst,
// #   bounded ~1000 iterations with the min(1000, num) trick for V <= 10^6).
// # - Sweep: O(n * F) updates.
// # Overall O(n * sqrt(V)) worst-case editorial bound, O(n * constant) for fixed V cap.
// #
// # Space complexity
// # - O(P) for distinct primes in the whole array (P <= total prime factors across nums), plus O(n)
// #   only implicitly through recursion stack none — O(P) counters.
// #
// # Edge cases
// # - n == 2: only i = 0 is candidate.
// # - Value 1: no primes; does not create spanning by itself.
// # - All numbers share a prime (e.g. all even): no valid split -> -1.
// # - Pairwise coprime consecutive groups: early split often at smallest i.
// #
// # Tests (mental / small)
// # - [3, 5]: split after 0 -> gcd(3,5)=1 -> answer 0.
// # - [2, 4]: share factor 2 -> -1.
// #
// # Improvements
// # - Precompute smallest-prime-factor (SPF) sieve up to max(nums) for O(log n) factorization per value.
// # - Interval-merge variant: record first/last index per prime, sweep mx last index — same goal,
// #   alternative implementation (good for interviews).
// #
// # LeetCode submission
// # Place imports (`collections`, `typing.List`) inside # lc-original code=start so the judge bundle runs.
// #
// # Interview walkthrough
// # 1) gcd(products)=1 <=> no shared prime between sides.
// # 2) Sweep i; maintain whether any prime still appears on both sides using counts.
// # 3) Factor integers without big integers; trial division or SPF.
// # 4) Complexity and edge case nums[i]==1.
// # --- end notes ---
// 
// # lc-original code=start
// import collections
// from typing import List
// 
// 
// class Solution:
//     def findValidSplit(self, nums: List[int]) -> int:
//         def prime_factors(num: int) -> List[int]:
//             """Distinct prime factors of num (LC: nums[i] <= 10^6 -> trial divide up to 1000 suffices)."""
//             if num <= 1:
//                 return []
//             factors: List[int] = []
//             x = num
//             for d in range(2, min(1000, x) + 1):
//                 if x % d == 0:
//                     factors.append(d)
//                     while x % d == 0:
//                         x //= d
//             if x > 1:
//                 factors.append(x)
//             return factors
// 
//         right = collections.Counter()
//         for v in nums:
//             for p in prime_factors(v):
//                 right[p] += 1
// 
//         left_bridge = collections.Counter()
// 
//         for i in range(len(nums) - 1):
//             for p in prime_factors(nums[i]):
//                 right[p] -= 1
//                 if right[p] == 0:
//                     right.pop(p)
//                     left_bridge.pop(p, None)
//                 else:
//                     left_bridge[p] += 1
//             if not left_bridge:
//                 return i
// 
//         return -1
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
    vector<int> primeFactors(int num) {
        vector<int> factors;
        if (num <= 1) return factors;
        int x = num;
        for (int d = 2; d <= min(1000, x); ++d) {
            if (x % d == 0) {
                factors.push_back(d);
                while (x % d == 0) x /= d;
            }
        }
        if (x > 1) factors.push_back(x);
        return factors;
    }

public:
    int findValidSplit(vector<int>& nums) {
        unordered_map<int, int> right, bridge;
        for (int v : nums) for (int p : primeFactors(v)) ++right[p];
        for (int i = 0; i + 1 < (int)nums.size(); ++i) {
            for (int p : primeFactors(nums[i])) {
                if (--right[p] == 0) {
                    right.erase(p);
                    bridge.erase(p);
                } else {
                    ++bridge[p];
                }
            }
            if (bridge.empty()) return i;
        }
        return -1;
    }
};
// @lc code=end
