/*
 * @lc app=leetcode id=3855 lang=cpp
 *
 * [3855] Sum of K-Digit Numbers in a Range
 */
// Translated from 3855.sum-of-k-digit-numbers-in-a-range.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3855 lang=python3
// #
// # [3855] Sum of K-Digit Numbers in a Range
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given three integers l, r, and k.
// #
// # Build every possible k-digit sequence where each digit is independently chosen
// # from the inclusive digit range [l, r]. If 0 is included, leading zeros are
// # allowed. Interpret each sequence as a normal integer and return the sum of all
// # such integers modulo 1_000_000_007.
// #
// # Example:
// #   l = 1, r = 2, k = 2
// #   sequences: 11, 12, 21, 22
// #   sum = 66
// #
// # Another example:
// #   l = 0, r = 1, k = 3
// #   sequences: 000, 001, 010, 011, 100, 101, 110, 111
// #   numeric sum = 0 + 1 + 10 + 11 + 100 + 101 + 110 + 111 = 444
// #
// #
// # Why brute force is impossible
// # The number of sequences is:
// #   (r - l + 1)^k
// #
// # k can be as large as 10^9. Even with at most 10 digit choices, generating all
// # sequences is impossible. We need a direct counting formula.
// #
// #
// # Key observation: contribution by digit position
// # Let:
// #   cnt = r - l + 1
// #   digit_sum = l + (l + 1) + ... + r
// #
// # Consider one fixed position, for example the tens place.
// #
// # At that position:
// #   - every allowed digit appears the same number of times,
// #   - the remaining k - 1 positions are free,
// #   - so each digit appears cnt^(k - 1) times.
// #
// # Therefore, the total digit value contributed at any one position is:
// #   digit_sum * cnt^(k - 1)
// #
// # The only difference between positions is place value:
// #   ones place       = 1
// #   tens place       = 10
// #   hundreds place   = 100
// #   ...
// #   highest position = 10^(k - 1)
// #
// # So the total answer is:
// #   digit_sum * cnt^(k - 1) * (1 + 10 + 10^2 + ... + 10^(k - 1))
// #
// #
// # Geometric sum
// # The place-value sum is a repunit:
// #   1 + 10 + 10^2 + ... + 10^(k - 1)
// #     = (10^k - 1) / 9
// #
// # Since we are working modulo MOD = 1_000_000_007, division by 9 means multiply
// # by the modular inverse of 9:
// #   inv9 = pow(9, MOD - 2, MOD)
// #
// # This works because MOD is prime and 9 is not divisible by MOD.
// #
// #
// # Final formula
// #   answer =
// #       digit_sum
// #       * cnt^(k - 1)
// #       * ((10^k - 1) / 9)
// #
// # All operations are done modulo MOD.
// #
// #
// # Walkthrough of the code
// # 1. Compute cnt = r - l + 1.
// # 2. Compute digit_sum using the arithmetic-series formula:
// #      (l + r) * cnt // 2
// #    This is an exact integer before modulo.
// # 3. Compute ways_for_other_positions = cnt^(k - 1) mod MOD.
// # 4. Compute repunit = (10^k - 1) / 9 mod MOD.
// # 5. Multiply the three pieces modulo MOD.
// #
// #
// # Correctness proof
// #
// # Lemma 1: For any fixed position, each digit d in [l, r] appears cnt^(k - 1)
// # times among all valid sequences.
// # Proof:
// # Fix that position to digit d. Every one of the other k - 1 positions can be
// # chosen independently in cnt ways. Therefore there are cnt^(k - 1) sequences
// # with digit d at this fixed position.
// #
// # Lemma 2: The total numeric contribution from one position with place value P is
// # digit_sum * cnt^(k - 1) * P.
// # Proof:
// # By Lemma 1, digit d appears cnt^(k - 1) times at this position. Each appearance
// # contributes d * P to the numeric value. Summing over all allowed digits gives:
// #   P * cnt^(k - 1) * sum(d for d in [l, r])
// # which is exactly digit_sum * cnt^(k - 1) * P.
// #
// # Lemma 3: The sum of all place values in a k-digit sequence is
// # 1 + 10 + 10^2 + ... + 10^(k - 1).
// # Proof:
// # The rightmost digit has place value 1, the next has 10, and so on up to
// # 10^(k - 1).
// #
// # Theorem: The algorithm returns the sum of all valid numbers.
// # Proof:
// # By Lemma 2, each position contributes
// # digit_sum * cnt^(k - 1) * place_value. Summing this over all positions and
// # applying Lemma 3 gives:
// #   digit_sum * cnt^(k - 1) * (1 + 10 + ... + 10^(k - 1))
// # This is exactly the formula used by the algorithm. Modular arithmetic preserves
// # addition and multiplication, so the returned value is the required sum modulo
// # MOD.
// #
// #
// # Complexity analysis
// #
// # Time:
// #   pow(cnt, k - 1, MOD) takes O(log k).
// #   pow(10, k, MOD) takes O(log k).
// #   All other work is O(1).
// # Overall time complexity: O(log k).
// #
// # Space:
// #   The algorithm uses only a fixed number of integer variables.
// # Overall space complexity: O(1).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Basic example:
// #      l = 1, r = 2, k = 2 -> 66
// #
// # 2. Leading zeros allowed:
// #      l = 0, r = 1, k = 3 -> 444
// #
// # 3. Single digit choice:
// #      l = 5, r = 5, k = 10 -> 555555520
// #      There is only one sequence: 5555555555.
// #
// # 4. k = 1:
// #      l = 3, r = 7, k = 1 -> 3 + 4 + 5 + 6 + 7 = 25
// #      Formula works because cnt^(k - 1) = cnt^0 = 1 and repunit = 1.
// #
// # 5. Only zero:
// #      l = 0, r = 0, any k -> 0
// #
// # 6. Full digit range:
// #      l = 0, r = 9, k = 1 -> 45
// #
// #
// # Edge cases
// #
// # - l == r: only one repeated-digit number exists.
// # - l == r == 0: answer is 0 for every k.
// # - k is huge: handled by modular exponentiation, never by looping k times.
// # - Leading zeros: no special handling is needed. A leading zero simply
// #   contributes 0 at its place value, and it is naturally included in digit_sum.
// #
// #
// # Possible improvements
// #
// # - inv9 could be hardcoded as 111111112, but computing it with pow keeps the
// #   code self-explanatory.
// # - Since l and r are digits, digit_sum is tiny. Keeping it as an exact integer
// #   before taking modulo is simple and avoids any modular division by 2.
// # - There is no need for digit DP here because every position has the same
// #   independent digit choices and there are no upper/lower number-bound
// #   constraints beyond the per-position digit range.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// class Solution:
//     MOD = 1_000_000_007
// 
//     def sumOfNumbers(self, l: int, r: int, k: int) -> int:
//         mod = self.MOD
//         count = r - l + 1
//         digit_sum = (l + r) * count // 2
// 
//         other_positions = pow(count, k - 1, mod)
//         repunit = (pow(10, k, mod) - 1) * pow(9, mod - 2, mod) % mod
// 
//         return digit_sum % mod * other_positions % mod * repunit % mod
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
    static constexpr long long MOD = 1000000007LL;
    long long modPow(long long a, long long e) {
        long long r = 1;
        while (e) {
            if (e & 1) r = r * a % MOD;
            a = a * a % MOD;
            e >>= 1;
        }
        return r;
    }

public:
    int sumOfNumbers(long long l, long long r, int k) {
        long long count = r - l + 1;
        long long digitSum = (l + r) * count / 2;
        long long other = modPow(count % MOD, k - 1);
        long long repunit = (modPow(10, k) - 1 + MOD) % MOD * modPow(9, MOD - 2) % MOD;
        return digitSum % MOD * other % MOD * repunit % MOD;
    }
};
// @lc code=end
