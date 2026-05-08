// Translated from 3871.count-commas-in-range-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3871 lang=python3
// #
// # [3871] Count Commas in Range II
// #
// # https://leetcode.com/problems/count-commas-in-range-ii/description/
// #
// # algorithms
// # Medium (40.91%)
// # Likes:    57
// # Dislikes: 6
// # Total Accepted:    41.6K
// # Total Submissions: 101.7K
// # Testcase Example:  '1002'
// #
// # You are given an integer n.
// # 
// # Return the total number of commas used when writing all integers from [1, n]
// # (inclusive) in standard number formatting.
// # 
// # In standard formatting:
// # 
// # 
// # A comma is inserted after every three digits from the right.
// # Numbers with fewer than 4 digits contain no commas.
// # 
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: n = 1002
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # The numbers "1,000", "1,001", and "1,002" each contain one comma, giving a
// # total of 3.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: n = 998
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # ​​​​​​​All numbers from 1 to 998 have fewer than four digits. Therefore, no
// # commas are used.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n <= 10^15
// # 
// # 
// #
// 
// # @lc code=start
// class Solution:
//     def countCommas(self, n: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We write every integer from 1 to `n` using standard comma formatting and
//         count the total number of commas.
// 
//         Standard formatting inserts commas every three digits from the right:
// 
//             999          -> 0 commas
//             1,000        -> 1 comma
//             999,999      -> 1 comma
//             1,000,000    -> 2 commas
//             1,000,000,000 -> 3 commas
// 
//         We need the total comma count for all numbers in `[1, n]`.
// 
//         Key observation
//         ---------------
//         The number of commas depends only on how many digits the number has.
// 
//         More specifically, numbers are grouped into powers of 1000:
// 
//         * 1 to 999:
//               0 commas
// 
//         * 1,000 to 999,999:
//               1 comma
// 
//         * 1,000,000 to 999,999,999:
//               2 commas
// 
//         * 1,000,000,000 to 999,999,999,999:
//               3 commas
// 
//         and so on.
// 
//         For a number `x`, the comma count is:
// 
//             number of complete groups of 3 digits to the right of the first
//             group
// 
//         But instead of computing that for every x, we sum whole ranges at once.
// 
//         Range contribution
//         ------------------
//         Suppose we are counting numbers that each have exactly `commas` commas.
// 
//         For `commas = 1`, the range starts at:
// 
//             1000
// 
//         and ends at:
// 
//             1000^2 - 1 = 999999
// 
//         For `commas = 2`, the range starts at:
// 
//             1000^2 = 1000000
// 
//         and ends at:
// 
//             1000^3 - 1 = 999999999
// 
//         In general:
// 
//             start = 1000^commas
//             end   = 1000^(commas + 1) - 1
// 
//         Every number in that range contributes exactly `commas`.
// 
//         If `n` cuts the range short, we only count up to `n`:
// 
//             actual_end = min(n, end)
//             count = actual_end - start + 1
//             contribution = count * commas
// 
//         Algorithm
//         ---------
//         1. Initialize:
// 
//                answer = 0
//                start = 1000
//                commas = 1
// 
//         2. While `start <= n`:
//               - `end = start * 1000 - 1`
//               - `actual_end = min(n, end)`
//               - add `(actual_end - start + 1) * commas`
//               - move to the next block:
// 
//                     start *= 1000
//                     commas += 1
// 
//         3. Return `answer`.
// 
//         Data structure choice
//         ---------------------
//         No data structure is needed.  This is pure arithmetic over a small
//         number of digit blocks.
// 
//         Since `n <= 10^15`, there are only a few blocks:
// 
//             10^3, 10^6, 10^9, 10^12, 10^15
// 
//         So the loop runs at most 5 times.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Every integer from 1 to n that contains at least one comma
//         belongs to exactly one block `[1000^c, 1000^(c + 1) - 1]`, where `c` is
//         its number of commas.
//         Standard formatting creates one comma for each full group of three
//         digits after the leading group.  Numbers from `1000^c` up to
//         `1000^(c + 1) - 1` have exactly `c` such groups to the right of the
//         leading group.  The blocks are disjoint and cover all numbers at least
//         1000.
// 
//         Lemma 2: For each block, the algorithm adds exactly the total number of
//         commas contributed by numbers in that block up to n.
//         The algorithm computes the intersection of the block with `[1, n]` as
//         `[start, min(n, end)]`.  The number of integers in that intersection is
//         `actual_end - start + 1`, and each contributes exactly `commas`, so the
//         added product is exactly that block's contribution.
// 
//         Theorem: The algorithm returns the total number of commas used from 1 to
//         n.
//         Numbers below 1000 contribute 0.  By Lemma 1, every number that
//         contributes at least one comma belongs to exactly one processed block.
//         By Lemma 2, each block's contribution is counted exactly.  Therefore the
//         sum returned by the algorithm is the required total.
// 
//         Complexity analysis
//         -------------------
//         Let B be the number of comma blocks up to n.  Since each block multiplies
//         the boundary by 1000:
// 
//             B = O(log_1000 n)
// 
//         Total time:  O(log n)
//         Total space: O(1)
// 
//         Under the given constraint `n <= 10^15`, the loop runs at most 5 times.
// 
//         Edge cases
//         ----------
//         * n < 1000:
//           No number has a comma, so the answer is 0.
// 
//         * n exactly at a boundary:
//               n = 1000 includes exactly one number with one comma.
// 
//         * n just before a boundary:
//               n = 999999 only includes one-comma numbers, not two-comma
//               numbers.
// 
//         * Very large n:
//               n = 10^15 is still handled by a few arithmetic iterations.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               n = 1002 -> 3
//               n = 998  -> 0
// 
//         * Boundaries:
//               n = 999
//               n = 1000
//               n = 999999
//               n = 1000000
// 
//         * Small random n:
//           Compare against brute force using formatted strings.
// 
//         Possible improvement?
//         ---------------------
//         This block-summing approach is already optimal and simpler than digit DP.
//         A closed-form expression is possible, but the loop is clearer and only
//         runs a constant number of times for the constraints.
//         """
// 
//         answer = 0
//         start = 1000
//         commas = 1
// 
//         while start <= n:
//             end = start * 1000 - 1
//             actual_end = min(n, end)
//             answer += (actual_end - start + 1) * commas
// 
//             start *= 1000
//             commas += 1
// 
//         return answer
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
    long long countCommas(long long n) {
        long long ans = 0, start = 1000, commas = 1;
        while (start <= n) {
            long long end = start * 1000 - 1;
            long long actual = min(n, end);
            ans += (actual - start + 1) * commas;
            start *= 1000;
            ++commas;
        }
        return ans;
    }
};
