// Translated from 3791.number-of-balanced-integers-in-a-range.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3791 lang=python3
// #
// # [3791] Number of Balanced Integers in a Range
// #
// # https://leetcode.com/problems/number-of-balanced-integers-in-a-range/description/
// #
// # algorithms
// # Hard (35.57%)
// # Likes:    46
// # Dislikes: 3
// # Total Accepted:    7.9K
// # Total Submissions: 22.2K
// # Testcase Example:  '1\n100'
// #
// # You are given two integers low and high.
// # 
// # An integer is called balanced if it satisfies both of the following
// # conditions:
// # 
// # 
// # It contains at least two digits.
// # The sum of digits at even positions is equal to the sum of digits at odd
// # positions (the leftmost digit has position 1).
// # 
// # 
// # Return an integer representing the number of balanced integers in the range
// # [low, high] (both inclusive).
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: low = 1, high = 100
// # 
// # Output: 9
// # 
// # Explanation:
// # 
// # The 9 balanced numbers between 1 and 100 are 11, 22, 33, 44, 55, 66, 77, 88,
// # and 99.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: low = 120, high = 129
// # 
// # Output: 1
// # 
// # Explanation:
// # 
// # Only 121 is balanced because the sum of digits at even and odd positions are
// # both 2.
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: low = 1234, high = 1234
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # 1234 is not balanced because the sum of digits at odd positions (1 + 3 = 4)
// # does not equal the sum at even positions (2 + 4 = 6).
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= low <= high <= 10^15
// # 
// # 
// #
// 
// # @lc code=start
// from functools import lru_cache
// 
// 
// class Solution:
//     def countBalanced(self, low: int, high: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We need to count integers in `[low, high]` that are "balanced".
// 
//         A number is balanced when:
// 
//         * it has at least two digits
//         * the sum of digits in odd positions equals the sum of digits in even
//           positions
// 
//         Positions are counted from the left, starting at 1.
// 
//         Example:
// 
//             121
// 
//         Positions:
// 
//             position 1 -> digit 1
//             position 2 -> digit 2
//             position 3 -> digit 1
// 
//         Odd-position sum:
// 
//             1 + 1 = 2
// 
//         Even-position sum:
// 
//             2
// 
//         So 121 is balanced.
// 
//         Why digit DP?
//         -------------
//         `high` can be as large as `10^15`, so we cannot check every number in
//         the range.
// 
//         But `10^15` has only 16 digits.  That makes digit DP the natural tool:
//         count how many valid numbers are `<= x` without enumerating the numbers
//         themselves.
// 
//         Then:
// 
//             answer = count_up_to(high) - count_up_to(low - 1)
// 
//         Key modeling choice
//         -------------------
//         Since positions are counted from the leftmost actual digit, leading
//         zeros would make the position parity ambiguous.  Instead of doing one
//         DP over padded numbers, we count by exact length.
// 
//         For `count_up_to(x)`:
// 
//         * count every balanced number with length 2, 3, ..., len(x) - 1
//         * count balanced numbers with length exactly len(x) that are <= x
// 
//         This avoids leading-zero complications.
// 
//         DP state
//         --------
//         For a fixed digit array `digits`, where `digits` is either:
// 
//             [9, 9, ..., 9]       for unrestricted numbers of that length
// 
//         or:
// 
//             digits of x          for the same-length bounded case
// 
//         define:
// 
//             dfs(index, diff, tight)
// 
//         where:
// 
//         * `index` is the current digit position, 0-based
//         * `diff` is:
// 
//               odd_position_sum - even_position_sum
// 
//         * `tight` tells whether the prefix so far is equal to the upper bound's
//           prefix
// 
//         At the end, the number is balanced exactly when:
// 
//             diff == 0
// 
//         Transition
//         ----------
//         At each position, choose the next digit.
// 
//         * first digit cannot be 0
//         * if `tight` is true, the digit cannot exceed `digits[index]`
//         * otherwise, the digit can go up to 9
// 
//         If the 1-based position is odd, add the digit to `diff`.
//         If it is even, subtract the digit from `diff`.
// 
//         Data structure choice
//         ---------------------
//         We use memoized recursion with `lru_cache`.
// 
//         The same `(index, diff, tight)` states appear many times as different
//         prefixes lead to the same remaining subproblem.  Caching turns the
//         exponential search tree into a small dynamic program.
// 
//         The possible `diff` range is tiny:
// 
//             -9 * 16 <= diff <= 9 * 16
// 
//         because the maximum length is 16.
// 
//         Algorithm
//         ---------
//         1. Implement `count_fixed_length(digits)`, which counts balanced numbers
//            with exactly `len(digits)` digits and not greater than the bound
//            represented by `digits`.
// 
//         2. Implement `count_up_to(limit)`:
//               * if `limit < 10`, return 0 because balanced numbers need at
//                 least two digits
//               * for every shorter length, call `count_fixed_length([9] * length)`
//               * for the same length, call `count_fixed_length(limit_digits)`
// 
//         3. Return:
// 
//                count_up_to(high) - count_up_to(low - 1)
// 
//         Correctness proof
//         -----------------
//         Lemma 1: `count_fixed_length(digits)` counts exactly the balanced
//         positive integers with length `len(digits)` and value at most `digits`.
//         The DP chooses every valid digit sequence of that exact length: the
//         first digit is never zero, later digits may be zero, and the `tight`
//         flag enforces the upper bound.  The running `diff` is updated by adding
//         odd-position digits and subtracting even-position digits.  At the end,
//         `diff == 0` is exactly the balanced condition.
// 
//         Lemma 2: `count_up_to(limit)` counts exactly the balanced integers in
//         `[1, limit]`.
//         Every positive integer `<= limit` has either fewer digits than `limit`
//         or the same number of digits.  The function counts all shorter lengths
//         with all-9 bounds and counts the same length with `limit` as the bound.
//         These groups are disjoint and cover all possible lengths.  Length 1 is
//         excluded because balanced integers need at least two digits.
// 
//         Theorem: `countBalanced(low, high)` returns the number of balanced
//         integers in `[low, high]`.
//         By Lemma 2, `count_up_to(high)` counts all balanced integers up to
//         `high`, and `count_up_to(low - 1)` counts all balanced integers strictly
//         below `low`.  Subtracting leaves exactly the balanced integers in the
//         inclusive range `[low, high]`.
// 
//         Complexity analysis
//         -------------------
//         Let `L` be the number of digits in `high`.  Here `L <= 16`.
// 
//         For one fixed length:
// 
//         * `index` has O(L) values
//         * `diff` has O(9L) possible values
//         * `tight` has 2 values
//         * each state tries at most 10 digits
// 
//         Time per fixed-length DP:
// 
//             O(L * 9L * 2 * 10) = O(L^2)
// 
//         We run this for O(L) lengths, so:
// 
//             O(L^3)
// 
//         With `L <= 16`, this is extremely small.
// 
//         Space:
// 
//             O(L^2)
// 
//         for the memoization table of one fixed-length DP.
// 
//         Edge cases
//         ----------
//         * `limit < 10`:
//           No balanced numbers because at least two digits are required.
// 
//         * Ranges containing one-digit numbers:
//           They are ignored naturally by `count_up_to`.
// 
//         * `low == high`:
//           The subtraction still works and returns either 0 or 1.
// 
//         * Odd number of digits:
//           Allowed.  Odd positions may have one more digit than even positions;
//           we still compare sums.
// 
//         * Upper bound `10^15`:
//           It has 16 digits.  The DP handles it directly.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               low = 1,    high = 100  -> 9
//               low = 120,  high = 129  -> 1
//               low = 1234, high = 1234 -> 0
// 
//         * Single balanced value:
//               low = 11, high = 11 -> 1
// 
//         * Single unbalanced value:
//               low = 10, high = 10 -> 0
// 
//         * Small ranges compared with brute force.
//         * Large boundary such as high = 10^15 to ensure no overflow or
//           performance issue.
// 
//         Possible improvement
//         --------------------
//         The current digit DP is already fast enough.  A combinatorics solution
//         could precompute counts by length and digit sum, but digit DP is simpler,
//         less error-prone, and handles arbitrary bounds directly.
//         """
// 
//         def count_fixed_length(bound_digits: list[int]) -> int:
//             length = len(bound_digits)
// 
//             @lru_cache(None)
//             def dfs(index: int, diff: int, tight: bool) -> int:
//                 if index == length:
//                     return 1 if diff == 0 else 0
// 
//                 upper = bound_digits[index] if tight else 9
//                 lower = 1 if index == 0 else 0
//                 total = 0
// 
//                 for digit in range(lower, upper + 1):
//                     if index % 2 == 0:
//                         next_diff = diff + digit
//                     else:
//                         next_diff = diff - digit
// 
//                     total += dfs(
//                         index + 1,
//                         next_diff,
//                         tight and digit == upper,
//                     )
// 
//                 return total
// 
//             return dfs(0, 0, True)
// 
//         def count_up_to(limit: int) -> int:
//             if limit < 10:
//                 return 0
// 
//             digits = [int(char) for char in str(limit)]
//             total = 0
// 
//             for length in range(2, len(digits)):
//                 total += count_fixed_length([9] * length)
// 
//             total += count_fixed_length(digits)
//             return total
// 
//         return count_up_to(high) - count_up_to(low - 1)
// # @lc code=end
// 
// 
// if __name__ == "__main__":
//     def is_balanced(value: int) -> bool:
//         digits = [int(char) for char in str(value)]
//         if len(digits) < 2:
//             return False
// 
//         odd_sum = sum(digits[index] for index in range(0, len(digits), 2))
//         even_sum = sum(digits[index] for index in range(1, len(digits), 2))
//         return odd_sum == even_sum
// 
//     def brute_force_count(low: int, high: int) -> int:
//         return sum(1 for value in range(low, high + 1) if is_balanced(value))
// 
//     solution = Solution()
// 
//     fixed_tests = [
//         (1, 100, 9),
//         (120, 129, 1),
//         (1234, 1234, 0),
//         (11, 11, 1),
//         (10, 10, 0),
//         (1, 9, 0),
//         (1, 99, 9),
//         (1000, 9999, brute_force_count(1000, 9999)),
//     ]
// 
//     for test_low, test_high, expected in fixed_tests:
//         assert solution.countBalanced(test_low, test_high) == expected
// 
//     brute_force_ranges = [
//         (1, 250),
//         (95, 205),
//         (900, 1300),
//         (9990, 10050),
//     ]
// 
//     for test_low, test_high in brute_force_ranges:
//         expected = brute_force_count(test_low, test_high)
//         assert solution.countBalanced(test_low, test_high) == expected
// 
//     assert solution.countBalanced(1, 10**15) >= 0

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
    long long countFixed(const vector<int>& digits) {
        int len = digits.size();
        map<tuple<int, int, bool>, long long> memo;
        function<long long(int, int, bool)> dfs = [&](int idx, int diff, bool tight) -> long long {
            if (idx == len) return diff == 0;
            auto key = make_tuple(idx, diff, tight);
            if (memo.count(key)) return memo[key];
            int up = tight ? digits[idx] : 9;
            int low = idx == 0 ? 1 : 0;
            long long total = 0;
            for (int d = low; d <= up; ++d) total += dfs(idx + 1, diff + (idx % 2 == 0 ? d : -d), tight && d == up);
            return memo[key] = total;
        };
        return dfs(0, 0, true);
    }

    long long upTo(long long limit) {
        if (limit < 10) return 0;
        string s = to_string(limit);
        vector<int> digits;
        for (char c : s) digits.push_back(c - '0');
        long long total = 0;
        for (int len = 2; len < (int)digits.size(); ++len) total += countFixed(vector<int>(len, 9));
        total += countFixed(digits);
        return total;
    }

public:
    long long countBalanced(long long low, long long high) {
        return upTo(high) - upTo(low - 1);
    }
};
