/*
 * @lc app=leetcode id=3918 lang=cpp
 *
 * [3918] Sum of Primes Between Number and Its Reverse
 */
// Translated from 3918.sum-of-primes-between-number-and-its-reverse.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3918 lang=python3
// #
// # [3918] Sum of Primes Between Number and Its Reverse
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given an integer n.
// #
// # Let r be the integer formed by reversing the decimal digits of n.
// #
// # Return the sum of all prime numbers in:
// #   [min(n, r), max(n, r)]
// #
// # inclusive.
// #
// # Example:
// #   n = 13
// #   r = 31
// #   primes in [13, 31] are 13, 17, 19, 23, 29, 31
// #   sum = 132
// #
// #
// # Constraints and algorithm choice
// # n <= 1000.
// #
// # Reversing the digits of a number <= 1000 also gives a number <= 1000:
// #   1000 -> 1
// #   999  -> 999
// #
// # So the whole range is always inside [1, 1000].
// #
// # We can solve this very simply by:
// #   1. reversing n,
// #   2. building a prime table with the Sieve of Eratosthenes,
// #   3. building a prefix sum of primes,
// #   4. answering the range sum in O(1).
// #
// # A direct primality test for each number in the range would also pass because
// # the bound is tiny, but the sieve + prefix sum is a standard, clean technique
// # and scales better if the bound increases.
// #
// #
// # Reversing the number
// # Python string reversal is concise:
// #   int(str(n)[::-1])
// #
// # Leading zeros after reversal disappear automatically:
// #   n = 10 -> "01" -> 1
// #
// # That matches the problem's definition of r as an integer.
// #
// #
// # Sieve of Eratosthenes
// # Create an array is_prime where:
// #   is_prime[x] is True iff x is prime.
// #
// # Initially mark everything >= 2 as prime.
// # For each p from 2 to sqrt(limit):
// #   if p is prime, mark multiples p*p, p*p+p, ... as composite.
// #
// # We start at p*p because smaller multiples of p were already marked by smaller
// # prime factors.
// #
// #
// # Prefix sum of primes
// # Let:
// #   prime_prefix[i] = sum of primes <= i
// #
// # Then sum of primes in [left, right] is:
// #   prime_prefix[right] - prime_prefix[left - 1]
// #
// # This is useful even though there is only one query here because it makes the
// # range-sum logic explicit and avoids repeatedly checking primality.
// #
// #
// # Data structure choice
// # We use simple arrays:
// #   - is_prime: boolean list
// #   - prime_prefix: integer list
// #
// # Arrays are ideal because the numeric range is small and dense.
// #
// #
// # Walkthrough of the code
// # 1. reverse n into r.
// # 2. left = min(n, r), right = max(n, r).
// # 3. Sieve primes up to right.
// # 4. Build prefix sums of prime values.
// # 5. Return prefix[right] - prefix[left - 1].
// #
// #
// # Correctness proof
// #
// # Lemma 1: The sieve correctly identifies prime numbers up to limit.
// # Proof:
// # Every composite number x has some prime factor p <= sqrt(x). When the sieve
// # reaches that p, it marks x as a multiple of p. Prime numbers have no smaller
// # factor and are never marked composite.
// #
// # Lemma 2: prime_prefix[i] equals the sum of all primes from 1 through i.
// # Proof:
// # The recurrence:
// #   prime_prefix[i] = prime_prefix[i-1] + i if i is prime
// #                   = prime_prefix[i-1] otherwise
// # adds exactly the prime values and skips non-primes.
// #
// # Lemma 3: prime_prefix[right] - prime_prefix[left-1] equals the sum of primes
// # in [left, right].
// # Proof:
// # prime_prefix[right] contains all primes <= right. Subtracting
// # prime_prefix[left-1] removes all primes < left, leaving exactly primes in the
// # desired interval.
// #
// # Theorem: The algorithm returns the required sum.
// # Proof:
// # It computes the correct reversed integer r, chooses the required inclusive
// # interval, uses Lemma 1 to identify primes, and Lemmas 2 and 3 to sum exactly
// # the primes in that interval.
// #
// #
// # Complexity analysis
// #
// # Let R = max(n, reverse(n)). Here R <= 1000.
// #
// # Time:
// #   Sieve: O(R log log R)
// #   Prefix sum: O(R)
// #   Overall: O(R log log R)
// #
// # Space:
// #   is_prime and prime_prefix are O(R).
// #
// # With the given constraints, this is effectively constant time and space.
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      n = 13 -> reverse 31 -> sum primes [13,31] = 132
// #
// # 2. Example 2:
// #      n = 10 -> reverse 1 -> sum primes [1,10] = 17
// #
// # 3. Example 3:
// #      n = 8 -> reverse 8 -> range [8,8], no prime -> 0
// #
// # 4. Single prime palindrome:
// #      n = 7 -> range [7,7] -> 7
// #
// # 5. Leading-zero reversal:
// #      n = 1000 -> reverse 1 -> range [1,1000]
// #
// #
// # Edge cases
// #
// # - n = 1: reverse is 1; no primes in [1,1], answer 0.
// # - n equals its reverse: range has one number.
// # - reverse may be smaller than n, so use min/max.
// #
// #
// # Possible improvements
// #
// # - For one tiny query, trial division over the interval is acceptable.
// # - If many queries were asked, precomputing prime prefix once up to 1000 would
// #   answer each in O(1).
// # - If n were much larger, the same sieve approach works up to moderate limits;
// #   for huge limits, segmented sieve would be the natural upgrade.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// class Solution:
//     def sumOfPrimesInRange(self, n: int) -> int:
//         reversed_n = int(str(n)[::-1])
//         left = min(n, reversed_n)
//         right = max(n, reversed_n)
// 
//         is_prime = self._sieve(right)
//         prefix = [0] * (right + 1)
// 
//         for value in range(1, right + 1):
//             prefix[value] = prefix[value - 1] + (value if is_prime[value] else 0)
// 
//         return prefix[right] - (prefix[left - 1] if left > 0 else 0)
// 
//     def _sieve(self, limit: int) -> list[bool]:
//         if limit < 2:
//             return [False] * (limit + 1)
// 
//         is_prime = [True] * (limit + 1)
//         is_prime[0] = False
//         is_prime[1] = False
// 
//         p = 2
//         while p * p <= limit:
//             if is_prime[p]:
//                 for multiple in range(p * p, limit + 1, p):
//                     is_prime[multiple] = False
//             p += 1
// 
//         return is_prime
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
    vector<int> sieve(int limit) {
        vector<int> prime(limit + 1, limit >= 2);
        if (limit >= 0) prime[0] = 0;
        if (limit >= 1) prime[1] = 0;
        for (int p = 2; p * p <= limit; ++p) if (prime[p]) for (int q = p * p; q <= limit; q += p) prime[q] = 0;
        return prime;
    }

public:
    long long sumOfPrimesInRange(int n) {
        string s = to_string(n);
        reverse(s.begin(), s.end());
        int rn = stoi(s);
        int l = min(n, rn), r = max(n, rn);
        auto prime = sieve(r);
        vector<long long> pref(r + 1);
        for (int i = 1; i <= r; ++i) pref[i] = pref[i - 1] + (prime[i] ? i : 0);
        return pref[r] - (l > 0 ? pref[l - 1] : 0);
    }
};
// @lc code=end
