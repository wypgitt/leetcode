/*
 * @lc app=leetcode id=793 lang=cpp
 *
 * [793] Preimage Size of Factorial Zeroes Function
 */
// Translated from 793.preimage-size-of-factorial-zeroes-function.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=793 lang=python3
// #
// # [793] Preimage Size of Factorial Zeroes Function
// #
// # --- Notes (problem restatement, math, complexity, interview walkthrough) ---
// #
// # Problem restatement
// # Let Z(n) = number of trailing zeros in n! (with 0! = 1 so Z(0) = 0).
// # For a given k, count how many n >= 0 satisfy Z(n) = k.
// #
// # Why this is not "enumerate n"
// # Z(n) grows with n, but not by 1 each step. At n = 25, Z jumps from 4 to 6, so k = 5
// # never occurs. So the answer is not "scan n until Z(n) > k" without care—we need a
// # fast existence check and the size of the preimage.
// #
// # Math: what is Z(n)?
// # Trailing zeros come from factors 10 = 2 * 5. In n!, factors of 2 outnumber factors
// # of 5, so:
// #   Z(n) = sum_{i >= 1} floor(n / 5^i)
// # (Legendre's formula for the exponent of 5 in n!.)
// # Compute Z(n) in a loop: repeatedly n //= 5 and add n until n == 0. No extra data
// # structure—just O(log_5 n) iterations.
// #
// # Key structural facts (what makes the answer 0 or 5)
// # - Z(n) is non-decreasing in n.
// # - Z(n+1) - Z(n) is v_5(n+1) (how many times 5 divides n+1). So the jump at a
// #   multiple of 5 can be 1, 2, 3, ... (e.g. at 25 the jump is 2).
// # - Therefore some integers k are missing ("gaps").
// # - If k is achieved, the set { n : Z(n) = k } is a contiguous block of integers.
// #   Whenever k is in the image of Z, that block has length exactly 5 (answer is 0 or 5).
// # So:
// #   Either no n has Z(n) = k  -> return 0.
// #   Or exactly 5 values of n do -> return 5.
// # You do not need to find all five; you only need to know whether k is attainable.
// #
// # Algorithm: binary search for the smallest n with Z(n) >= k
// # Let m = min { n >= 0 : Z(n) >= k }.
// # - If Z(m) != k, then k is in a gap (first time we reach >= k we already overshoot k)
// #   -> 0.
// # - If Z(m) = k, then k is achievable -> preimage size 5.
// #
// # Monotonicity: Z(n) is non-decreasing, so the predicate Z(n) >= k is monotone in n
// # -> binary search is valid.
// #
// # Search bounds:
// # - lo = 0 always works.
// # - Z(5(k+1)) = (k+1) + Z(k+1) > k for k >= 0, so hi = 5(k+1) is always safe
// #   (LeetCode uses k <= 10^9; this hi is large enough).
// # Binary search pattern: first n with Z(n) >= k (lower bound).
// #
// # Complexity
// # Time: One Z(mid) costs O(log_5 mid). Binary search over [0, 5(k+1)] is O(log(5k))
// #   = O(log k) iterations. Total O(log k * log n) with n ~ O(k) in the search range
// #   -> O(log^2 k) in typical analysis; for k <= 10^9 this is tiny.
// # Space: O(1) extra (only a few integers).
// # Python integers are unbounded, so no overflow issues for these ranges.
// #
// # Why binary search (interview talking points)
// # - Direct scan of n is too slow for large k.
// # - Z is monotone, so "first n with Z(n) >= k" is a classic lower_bound on a monotone
// #   predicate.
// # - No DP or fancy structure; the only "structure" is monotonicity of Z.
// #
// # Edge cases to mention
// # - k = 0: Z(0)=...=Z(4)=0 -> five values -> 5. Search finds smallest n with Z(n) >= 0,
// #   which is 0, and Z(0)=0.
// # - k in a gap (e.g. 5): smallest n with Z(n) >= 5 is 25, Z(25)=6 != 5 -> 0.
// # - Large k (e.g. 10^9): same code; hi = 5(k+1) still works; Z loop remains O(log n).
// #
// # Tests (mental or unit)
// #   # Z(24)=4, Z(25)=6 -> k=5 unreachable
// #   assert preimageSizeFZF(5) == 0
// #   # k=0: n in {0,1,2,3,4}
// #   assert preimageSizeFZF(0) == 5
// #   assert preimageSizeFZF(4) == 5
// #   assert preimageSizeFZF(6) == 5
// #
// # Possible improvements / variants
// # - hi for k=0: Using hi = 5(k+1) already covers k=0 (hi=5); no special case required.
// # - Avoid double Z(lo): keep last mid or combine checks; gain is tiny vs clarity.
// # - Math-heavy alternative: characterize gaps (k unreachable iff ...) and answer 0/5
// #   without search—possible but error-prone in an interview; binary search + Z(n) is
// #   standard.
// #
// # How to walk through the code in an interview
// # 1. Define Z(n) and implement it in O(log n).
// # 2. State monotonicity and the 0-or-5 preimage fact (or verify k via first n with
// #    Z(n) >= k).
// # 3. Binary search m = min n : Z(n) >= k on [0, 5(k+1)].
// # 4. Return 5 if Z(m) == k else 0.
// # 5. Discuss time (log k * cost of Z), space O(1), edge cases k=0 and gap k=5.
// # --- end notes ---
// 
// # lc-original code=start
// class Solution:
//     def preimageSizeFZF(self, k: int) -> int:
//         def trailing_zeros_factorial(n: int) -> int:
//             """Exponent of 5 in n! (equals trailing zeros of n!): sum floor(n/5^i)."""
//             z = 0
//             while n:
//                 n //= 5
//                 z += n
//             return z
// 
//         # Smallest n with Z(n) >= k. If that Z(n) equals k, k is achievable → answer 5; else 0.
//         lo, hi = 0, 5 * (k + 1)
//         while lo < hi:
//             mid = (lo + hi) // 2
//             if trailing_zeros_factorial(mid) < k:
//                 lo = mid + 1
//             else:
//                 hi = mid
//         return 5 if trailing_zeros_factorial(lo) == k else 0
// 
// 
// # lc-original code=end
//

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
    long long zeros(long long n) {
        long long z = 0;
        while (n) {
            n /= 5;
            z += n;
        }
        return z;
    }

public:
    int preimageSizeFZF(int k) {
        long long lo = 0, hi = 5LL * (k + 1);
        while (lo < hi) {
            long long mid = (lo + hi) / 2;
            if (zeros(mid) < k) lo = mid + 1;
            else hi = mid;
        }
        return zeros(lo) == k ? 5 : 0;
    }
};
// @lc code=end
