// Translated from 668.kth-smallest-number-in-multiplication-table.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=668 lang=python3
// #
// # [668] Kth Smallest Number in Multiplication Table
// #
// # https://leetcode.com/problems/kth-smallest-number-in-multiplication-table/description/
// #
// # algorithms
// # Hard (54.08%)
// # Likes:    2283
// # Dislikes: 61
// # Total Accepted:    85.5K
// # Total Submissions: 158K
// # Testcase Example:  '3\n3\n5'
// #
// # Nearly everyone has used the Multiplication Table. The multiplication table
// # of size m x n is an integer matrix mat where mat[i][j] == i * j (1-indexed).
// # 
// # Given three integers m, n, and k, return the k^th smallest element in the m x
// # n multiplication table.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: m = 3, n = 3, k = 5
// # Output: 3
// # Explanation: The 5^th smallest number is 3.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: m = 2, n = 3, k = 6
// # Output: 6
// # Explanation: The 6^th smallest number is 6.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= m, n <= 3 * 10^4
// # 1 <= k <= m * n
// # 
// # 
// #
// 
// # @lc code=start
// class Solution:
//     def findKthNumber(self, m: int, n: int, k: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We have an `m x n` multiplication table:
// 
//             table[i][j] = i * j
// 
//         using 1-based indices:
// 
//             1 <= i <= m
//             1 <= j <= n
// 
//         We need the kth smallest value in this table.
// 
//         Why not build the table?
//         ------------------------
//         The constraints are large:
// 
//             m, n <= 30000
// 
//         The table can contain:
// 
//             30000 * 30000 = 900,000,000
// 
//         values.  Building and sorting that table is impossible in memory and too
//         slow.
// 
//         Key observation: binary search the answer
//         -----------------------------------------
//         The answer is a number between:
// 
//             1 and m * n
// 
//         If we choose a candidate value `x`, we can count how many entries in the
//         multiplication table are `<= x`.
// 
//         If at least `k` entries are `<= x`, then the kth smallest value is `<= x`.
//         Otherwise, the kth smallest value is `> x`.
// 
//         That monotonic yes/no property lets us binary search the smallest value
//         `x` such that:
// 
//             count_less_or_equal(x) >= k
// 
//         Counting entries <= x
//         ---------------------
//         Look at one row `i`.
// 
//         Row `i` is:
// 
//             i, 2i, 3i, ..., n*i
// 
//         The number of entries in this row that are `<= x` is:
// 
//             min(n, x // i)
// 
//         because:
// 
//             i * j <= x
//             j <= x // i
// 
//         and there are only `n` columns.
// 
//         So:
// 
//             count_less_or_equal(x)
//                 = sum(min(n, x // i) for i in 1..m)
// 
//         Optimization: iterate the smaller dimension
//         -------------------------------------------
//         The formula above scans rows.  We can swap `m` and `n` so that `m <= n`,
//         then scan only `m` rows.  The table values are the same under swapping
//         dimensions, and this improves performance when one dimension is much
//         smaller.
// 
//         Algorithm
//         ---------
//         1. If `m > n`, swap them so `m` is the smaller dimension.
//         2. Binary search over possible values:
// 
//                left = 1
//                right = m * n
// 
//         3. For each `mid`:
//               - compute how many table values are <= mid
//               - if count >= k, mid may be high enough, so move `right = mid`
//               - otherwise move `left = mid + 1`
// 
//         4. Return `left`.
// 
//         Why return the smallest feasible value?
//         ---------------------------------------
//         Duplicates exist in the multiplication table.  For example, `6` may
//         appear as `1*6`, `2*3`, `3*2`, and `6*1`.
// 
//         Because of duplicates, we should not try to find a value with count
//         exactly equal to `k`.  Instead, the kth smallest value is the smallest
//         number whose `<=` count reaches at least `k`.
// 
//         Data structure choice
//         ---------------------
//         No auxiliary data structure is needed.
// 
//         We use:
// 
//         * integer binary search boundaries
//         * a counting helper
// 
//         This keeps memory constant and avoids ever materializing the table.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: `count_less_or_equal(x)` returns the exact number of table
//         entries whose value is at most `x`.
//         In row `i`, entries are `i * 1, i * 2, ..., i * n`.  Exactly the first
//         `min(n, x // i)` of them are at most `x`.  Summing this exact count over
//         all rows counts every table entry once.
// 
//         Lemma 2: The predicate `count_less_or_equal(x) >= k` is monotonic.
//         If a value `x` has at least `k` table entries less than or equal to it,
//         then any larger value `y >= x` also has at least those same entries less
//         than or equal to it.  Therefore once the predicate becomes true, it stays
//         true.
// 
//         Lemma 3: The kth smallest table value is the smallest `x` such that
//         `count_less_or_equal(x) >= k`.
//         If fewer than `k` values are `<= x`, then the kth value must be greater
//         than `x`.  If at least `k` values are `<= x`, then the kth value is at
//         most `x`.  Therefore the first value where the count reaches `k` is
//         exactly the kth smallest value.
// 
//         Theorem: The algorithm returns the kth smallest value in the
//         multiplication table.
//         By Lemma 1, the counting function is exact.  By Lemma 2, the binary
//         search predicate is monotonic.  Binary search returns the smallest value
//         satisfying the predicate, and by Lemma 3 that value is exactly the kth
//         smallest table element.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             a = min(m, n)
//             b = max(m, n)
// 
//         Each count call scans `a` rows and costs O(a).
//         Binary search runs over values from 1 to `m * n`, so it takes:
// 
//             O(log(m * n))
// 
//         iterations.
// 
//         Total time:
// 
//             O(min(m, n) * log(m * n))
// 
//         Total space:
// 
//             O(1)
// 
//         Edge cases
//         ----------
//         * m = 1 or n = 1:
//           The table is just a sorted sequence of multiples, and the same binary
//           search/count logic works.
// 
//         * k = 1:
//           The answer is always 1.
// 
//         * k = m * n:
//           The answer is always m * n, and the binary search still finds it.
// 
//         * Duplicate values:
//           Counting `<= x` naturally includes duplicates, which is exactly how
//           kth order statistics in a table should work.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               m = 3, n = 3, k = 5 -> 3
//               m = 2, n = 3, k = 6 -> 6
// 
//         * Single row/column:
//               m = 1, n = 10, k = 7 -> 7
// 
//         * Small random tables:
//           Build the full table, sort it, and compare against this algorithm.
// 
//         * Large smoke tests:
//           Ensure performance remains fast for m, n near 30000.
// 
//         Possible improvement?
//         ---------------------
//         This is the standard optimal approach for the constraints.  There are
//         more advanced ways to speed up the counting step by grouping equal
//         quotients, but the simple O(min(m, n)) count is accepted, easier to
//         explain, and reliable in Python for these limits.
//         """
// 
//         if m > n:
//             m, n = n, m
// 
//         def count_less_or_equal(value: int) -> int:
//             count = 0
//             for row in range(1, m + 1):
//                 count += min(n, value // row)
//             return count
// 
//         left = 1
//         right = m * n
// 
//         while left < right:
//             middle = (left + right) // 2
// 
//             if count_less_or_equal(middle) >= k:
//                 right = middle
//             else:
//                 left = middle + 1
// 
//         return left
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
    int findKthNumber(int m, int n, int k) {
        if (m > n) swap(m, n);
        auto countLE = [&](int value) {
            int cnt = 0;
            for (int row = 1; row <= m; ++row) cnt += min(n, value / row);
            return cnt;
        };
        int lo = 1, hi = m * n;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (countLE(mid) >= k) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
};
