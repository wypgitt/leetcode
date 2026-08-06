/*
 * @lc app=leetcode id=397 lang=cpp
 *
 * [397] Integer Replacement
 */
// Translated from 397.integer-replacement.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=397 lang=python3
// #
// # [397] Integer Replacement
// #
// # https://leetcode.com/problems/integer-replacement/description/
// #
// # algorithms
// # Medium (37.47%)
// # Likes:    1448
// # Dislikes: 488
// # Total Accepted:    164.9K
// # Total Submissions: 439.9K
// # Testcase Example:  '8'
// #
// # Given a positive integer n, you can apply one of the following
// # operations:
// # 
// # 
// # If n is even, replace n with n / 2.
// # If n is odd, replace n with either n + 1 or n - 1.
// # 
// # 
// # Return the minimum number of operations needed for n to become 1.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: n = 8
// # Output: 3
// # Explanation: 8 -> 4 -> 2 -> 1
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: n = 7
// # Output: 4
// # Explanation: 7 -> 8 -> 4 -> 2 -> 1
// # or 7 -> 6 -> 3 -> 2 -> 1
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: n = 4
// # Output: 2
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n <= 2^31 - 1
// # 
// # 
// #
// 
// # lc-original code=start
// class Solution:
//     def integerReplacement(self, n: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We start with a positive integer `n`.  In one operation:
// 
//         * if `n` is even, we must replace it with `n / 2`
//         * if `n` is odd, we may replace it with either `n + 1` or `n - 1`
// 
//         Return the minimum number of operations needed to reach 1.
// 
//         Key idea
//         --------
//         Dividing by 2 is always good because it makes the number smaller
//         quickly.  So for even numbers, there is no choice:
// 
//             n = n // 2
// 
//         The only decision is when `n` is odd:
// 
//             should we use n - 1 or n + 1?
// 
//         After either choice, the result becomes even, so the next operation will
//         usually be one or more divisions by 2.  Therefore, for odd numbers, we
//         want to create a number with as many trailing zero bits as possible.
// 
//         Binary intuition
//         ----------------
//         In binary:
// 
//         * an even number ends in 0
//         * an odd number ends in 1
//         * dividing by 2 shifts right by one bit
// 
//         For an odd number greater than 1:
// 
//         * if it ends in `01`, subtracting 1 changes that suffix to `00`
//         * if it ends in `11`, adding 1 usually carries and creates more zeros
// 
//         Examples:
// 
//             9  = 1001
//             9 - 1 = 8  = 1000   good: three trailing zeros
//             9 + 1 = 10 = 1010   only one trailing zero
// 
//             15 = 1111
//             15 + 1 = 16 = 10000 good: four trailing zeros
//             15 - 1 = 14 = 1110  only one trailing zero
// 
//         The special case is:
// 
//             n = 3
// 
//         Although 3 ends in `11`, subtracting is better:
// 
//             3 -> 2 -> 1       2 operations
//             3 -> 4 -> 2 -> 1  3 operations
// 
//         Decision rule
//         -------------
//         While `n != 1`:
// 
//         1. If `n` is even, divide by 2.
//         2. If `n` is odd:
//               * if `n == 3`, subtract 1
//               * else if the last two bits are `01`, subtract 1
//               * else the last two bits are `11`, add 1
// 
//         How do we check the last two bits?
// 
//             n & 3
// 
//         because `3` is binary `11`.
// 
//         * `n & 3 == 1` means the number ends with `01`
//         * `n & 3 == 3` means the number ends with `11`
// 
//         Data structure choice
//         ---------------------
//         No complex data structure is needed.  We only keep:
// 
//         * the current number `n`
//         * the operation count `steps`
// 
//         This gives O(1) extra space.
// 
//         Alternative approaches
//         ----------------------
//         1. DFS with memoization:
//            Recurrence:
// 
//                f(1) = 0
//                f(n) = 1 + f(n / 2)                  if n is even
//                f(n) = 1 + min(f(n - 1), f(n + 1))   if n is odd
// 
//            This is very easy to prove correct and also efficient enough in
//            Python.  It uses O(log n) memo/recursion space.
// 
//         2. BFS:
//            Treat each number as a graph node and operations as edges.  BFS finds
//            the shortest path, but it explores unnecessary states and is less
//            elegant for this problem.
// 
//         3. Greedy bit rule:
//            Uses the binary structure directly and runs iteratively in O(log n)
//            time and O(1) space.  This is the approach implemented here.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: If `n` is even, every optimal solution starts by replacing
//         `n` with `n / 2`.
//         For even `n`, the problem gives only one legal operation, so all
//         solutions must take it.
// 
//         Lemma 2: For odd `n > 1`, after choosing `n - 1` or `n + 1`, the better
//         choice is the one that creates more trailing zero bits, except when
//         `n == 3`.
//         Both choices cost one operation and produce an even number.  More
//         trailing zero bits mean more immediate forced divisions by 2, reducing
//         the number faster without additional branching.  For odd numbers ending
//         in `01`, `n - 1` creates at least two trailing zeros.  For odd numbers
//         ending in `11`, `n + 1` creates at least two trailing zeros.  The only
//         exception is `3`, where subtracting reaches `2` and then `1` in fewer
//         operations than going through `4`.
// 
//         Lemma 3: The greedy rule makes an optimal choice at every odd `n`.
//         By Lemma 2, the rule chooses the branch that gives the strongest
//         immediate reduction through forced divisions by 2, except for `3`, where
//         the direct calculation shows subtracting is optimal.
// 
//         Theorem: The algorithm returns the minimum number of operations to
//         reach 1.
//         By Lemma 1, all even steps are forced.  By Lemma 3, every odd choice is
//         optimal.  Therefore the sequence of choices made by the algorithm is an
//         optimal sequence, and the counted number of steps is minimum.
// 
//         Complexity analysis
//         -------------------
//         Each even step divides `n` by 2.  Each odd step changes `n` by 1 and is
//         followed by at least one division by 2.  Therefore the number of loop
//         iterations is proportional to the number of bits in `n`.
// 
//         Time:
// 
//             O(log n)
// 
//         Space:
// 
//             O(1)
// 
//         Edge cases
//         ----------
//         * n = 1:
//           Already done, return 0.
// 
//         * n = 2:
//           One division: 2 -> 1.
// 
//         * n = 3:
//           Special case: 3 -> 2 -> 1 is better than 3 -> 4 -> 2 -> 1.
// 
//         * n = 2^31 - 1:
//           In fixed-width languages, `n + 1` may overflow.  Python integers do
//           not overflow, so the implementation is straightforward.  In Java/C++,
//           use a wider integer type such as `long`.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               8 -> 3
//               7 -> 4
//               4 -> 2
// 
//         * Base cases:
//               1 -> 0
//               2 -> 1
//               3 -> 2
// 
//         * Powers of two:
//               16 -> 4
// 
//         * Numbers where `+1` is best:
//               15 -> 5 via 15 -> 16 -> 8 -> 4 -> 2 -> 1
// 
//         * Maximum constraint:
//               2^31 - 1 -> 32
// 
//         Possible improvement
//         --------------------
//         The greedy solution is already optimal in time and space for this
//         problem.  A memoized recursive solution is often easier to derive first,
//         then the bit-greedy version is the polished interview answer.
//         """
// 
//         steps = 0
// 
//         while n != 1:
//             if n % 2 == 0:
//                 n //= 2
//             elif n == 3 or n & 3 == 1:
//                 n -= 1
//             else:
//                 n += 1
// 
//             steps += 1
// 
//         return steps
// # lc-original code=end
// 
// 
// if __name__ == "__main__":
//     solution = Solution()
// 
//     fixed_tests = {
//         1: 0,
//         2: 1,
//         3: 2,
//         4: 2,
//         7: 4,
//         8: 3,
//         9: 4,
//         15: 5,
//         16: 4,
//         2**31 - 1: 32,
//     }
// 
//     for value, expected in fixed_tests.items():
//         assert solution.integerReplacement(value) == expected, value
// 
//     def memoized_reference(value: int, memo: dict[int, int]) -> int:
//         if value == 1:
//             return 0
//         if value in memo:
//             return memo[value]
//         if value % 2 == 0:
//             memo[value] = 1 + memoized_reference(value // 2, memo)
//         else:
//             memo[value] = 1 + min(
//                 memoized_reference(value - 1, memo),
//                 memoized_reference(value + 1, memo),
//             )
//         return memo[value]
// 
//     for value in range(1, 200):
//         expected = memoized_reference(value, {})
//         assert solution.integerReplacement(value) == expected, value

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
    int integerReplacement(int n) {
        long long x = n;
        int steps = 0;
        while (x != 1) {
            if (x % 2 == 0) x /= 2;
            else if (x == 3 || (x & 3) == 1) --x;
            else ++x;
            ++steps;
        }
        return steps;
    }
};
// @lc code=end
