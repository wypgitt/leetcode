// Translated from 363.max-sum-of-rectangle-no-larger-than-k.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=363 lang=python3
// #
// # [363] Max Sum of Rectangle No Larger Than K
// #
// # https://leetcode.com/problems/max-sum-of-rectangle-no-larger-than-k/description/
// #
// # algorithms
// # Hard (45.53%)
// # Likes:    3580
// # Dislikes: 178
// # Total Accepted:    144.2K
// # Total Submissions: 316.6K
// # Testcase Example:  '[[1,0,1],[0,-2,3]]\n2'
// #
// # Given an m x n matrix matrix and an integer k, return the max sum of a
// # rectangle in the matrix such that its sum is no larger than k.
// # 
// # It is guaranteed that there will be a rectangle with a sum no larger than
// # k.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: matrix = [[1,0,1],[0,-2,3]], k = 2
// # Output: 2
// # Explanation: Because the sum of the blue rectangle [[0, 1], [-2, 3]] is 2,
// # and 2 is the max number no larger than k (k = 2).
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: matrix = [[2,2,-1]], k = 3
// # Output: 3
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # m == matrix.length
// # n == matrix[i].length
// # 1 <= m, n <= 100
// # -100 <= matrix[i][j] <= 100
// # -10^5 <= k <= 10^5
// # 
// # 
// # 
// # Follow up: What if the number of rows is much larger than the number of
// # columns?
// # 
// #
// 
// # @lc code=start
// from bisect import bisect_left
// from typing import List
// 
// 
// class FenwickTree:
//     def __init__(self, size: int):
//         self.size = size
//         self.tree = [0] * (size + 1)
// 
//     def add(self, index: int, delta: int) -> None:
//         while index <= self.size:
//             self.tree[index] += delta
//             index += index & -index
// 
//     def prefix_sum(self, index: int) -> int:
//         total = 0
//         while index > 0:
//             total += self.tree[index]
//             index -= index & -index
//         return total
// 
//     def find_by_order(self, order: int) -> int:
//         index = 0
//         bit = 1 << (self.size.bit_length() - 1)
// 
//         while bit:
//             next_index = index + bit
//             if next_index <= self.size and self.tree[next_index] < order:
//                 index = next_index
//                 order -= self.tree[next_index]
//             bit >>= 1
// 
//         return index + 1
// 
// 
// class Solution:
//     def maxSumSubmatrix(self, matrix: List[List[int]], k: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given an `m x n` matrix and an integer `k`.
// 
//         We need the maximum sum of any rectangular submatrix such that:
// 
//             rectangle_sum <= k
// 
//         The matrix may contain negative numbers, so we cannot use a simple
//         sliding window.
// 
//         High-level idea
//         ---------------
//         Convert the 2D problem into many 1D problems.
// 
//         If we fix two horizontal boundaries:
// 
//             top row
//             bottom row
// 
//         then every rectangle between those two rows is determined only by its
//         left and right columns.
// 
//         We can compress the rows between `top` and `bottom` into a 1D array:
// 
//             column_sums[col] = sum(matrix[row][col] for row in top..bottom)
// 
//         Now the sum of any rectangle with those fixed row boundaries is exactly
//         the sum of a contiguous subarray of `column_sums`.
// 
//         So the problem becomes:
// 
//             for each pair of boundaries,
//             find the maximum subarray sum no larger than k.
// 
//         Choosing the smaller dimension
//         ------------------------------
//         We can fix pairs of rows or pairs of columns.
// 
//         To minimize work, we square the smaller dimension:
// 
//         * if rows <= columns:
//               fix top/bottom rows and compress columns
// 
//         * if columns < rows:
//               fix left/right columns and compress rows
// 
//         This gives:
// 
//             O(min(rows, cols)^2 * max(rows, cols) * log(max(rows, cols)))
// 
//         rather than always squaring the row count.
// 
//         The 1D subproblem
//         -----------------
//         Given an array `nums`, find the largest subarray sum `<= k`.
// 
//         Use prefix sums:
// 
//             prefix[j] = nums[0] + nums[1] + ... + nums[j - 1]
// 
//         A subarray sum from `i` to `j - 1` is:
// 
//             prefix[j] - prefix[i]
// 
//         For the current prefix `current = prefix[j]`, we want a previous prefix
//         `previous = prefix[i]` such that:
// 
//             current - previous <= k
// 
//         Rearranging:
// 
//             previous >= current - k
// 
//         To maximize `current - previous` while staying <= k, we need the
//         smallest previous prefix that is at least `current - k`.
// 
//         That is an ordered-set query:
// 
//             lower_bound(current - k)
// 
//         Why Fenwick tree?
//         -----------------
//         Python's standard library does not include a balanced binary search tree.
//         A common Python solution uses a sorted list plus `bisect`, but inserting
//         into the middle of a list costs O(length).
// 
//         Here, the dimensions are small enough that the sorted-list version would
//         pass, but we can still keep the stronger ordered-set complexity by:
// 
//         1. computing all prefix sums for the current compressed 1D array
//         2. coordinate-compressing those prefix sums
//         3. using a Fenwick tree to store which prefix sums have already appeared
//         4. finding the first stored prefix rank at or after a lower bound
// 
//         The Fenwick tree stores counts of prefix-sum ranks.  It supports:
// 
//         * add one seen prefix: O(log L)
//         * count seen prefixes before a rank: O(log L)
//         * find the first seen rank by order statistic: O(log L)
// 
//         1D algorithm
//         ------------
//         For `nums`:
// 
//         1. Build all prefix sums and sort their unique values.
//         2. Add prefix sum 0 as already seen.
//         3. Scan `nums`, updating the running prefix `current`.
//         4. Let `needed = current - k`.
//         5. Find the first compressed prefix value >= `needed` that has been
//            seen.
//         6. If it exists, update the best answer with:
// 
//                current - previous_prefix
// 
//         7. Add `current` to the Fenwick tree.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For fixed top/bottom row boundaries, every rectangle between
//         those rows corresponds to exactly one contiguous subarray of
//         `column_sums`.
//         The rectangle's left and right columns choose a contiguous range of
//         columns.  Summing `column_sums` over that range equals the sum of all
//         cells in the rectangle.
// 
//         Lemma 2: The 1D helper returns the maximum subarray sum no larger than
//         `k`.
//         For each ending position, the helper considers the current prefix sum.
//         Any subarray ending here is `current - previous` for some previously
//         seen prefix.  The condition `current - previous <= k` is equivalent to
//         `previous >= current - k`.  Choosing the smallest seen previous prefix
//         satisfying that lower bound gives the largest valid subarray ending at
//         this position.  The helper checks every ending position, so it finds the
//         best valid subarray overall.
// 
//         Lemma 3: The outer loops consider every rectangle in the matrix.
//         If we fix row pairs, every rectangle has some top and bottom row pair,
//         and then Lemma 1 covers its columns.  If we fix column pairs instead, the
//         symmetric argument covers every rectangle by left/right boundaries and a
//         contiguous range of rows.
// 
//         Theorem: The algorithm returns the maximum rectangle sum no larger than
//         `k`.
//         By Lemma 3, every rectangle is represented in one compressed 1D problem.
//         By Lemma 2, each compressed problem contributes its best valid subarray
//         sum.  Taking the maximum over all boundary pairs therefore gives the
//         maximum valid rectangle sum.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             small = min(rows, cols)
//             large = max(rows, cols)
// 
//         There are O(small^2) boundary pairs.  For each pair, the compressed array
//         has length `large`, and the 1D helper costs O(large log large).
// 
//         Total time:
// 
//             O(small^2 * large * log large)
// 
//         Total space:
// 
//             O(large)
// 
//         for the compressed sums, prefix sums, coordinate-compressed values, and
//         Fenwick tree.
// 
//         Edge cases
//         ----------
//         * Negative numbers:
//           Prefix-sum ordered search handles negatives naturally.
// 
//         * k is negative:
//           We still search for sums no larger than k; no special case is needed.
// 
//         * Single row or single column:
//           The algorithm becomes exactly the 1D maximum-subarray-no-larger-than-k
//           problem.
// 
//         * Exact match:
//           If we ever find a rectangle sum equal to k, we can return immediately,
//           because no valid answer can be larger than k.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [[1,0,1],[0,-2,3]], k = 2 -> 2
//               [[2,2,-1]],          k = 3 -> 3
// 
//         * All negative values.
//         * Single row and single column.
//         * Random small matrices compared with brute-force rectangle enumeration.
// 
//         Possible improvement?
//         ---------------------
//         This is the standard optimal approach for this problem class.  In
//         languages with a built-in balanced tree, the 1D helper is usually written
//         with a TreeSet.  The Fenwick tree here gives the same ordered-prefix
//         behavior using only Python's standard library.
//         """
// 
//         row_count = len(matrix)
//         col_count = len(matrix[0])
// 
//         def best_subarray_no_larger_than(limit_values: List[int]) -> int:
//             prefix = 0
//             prefixes = [0]
// 
//             for value in limit_values:
//                 prefix += value
//                 prefixes.append(prefix)
// 
//             sorted_prefixes = sorted(set(prefixes))
//             fenwick = FenwickTree(len(sorted_prefixes))
// 
//             best = -10**18
//             prefix = 0
//             zero_rank = bisect_left(sorted_prefixes, 0) + 1
//             fenwick.add(zero_rank, 1)
// 
//             for value in limit_values:
//                 prefix += value
//                 lower_bound = prefix - k
//                 lower_index = bisect_left(sorted_prefixes, lower_bound)
// 
//                 seen_before = fenwick.prefix_sum(lower_index)
//                 total_seen = fenwick.prefix_sum(len(sorted_prefixes))
// 
//                 if total_seen > seen_before:
//                     rank = fenwick.find_by_order(seen_before + 1)
//                     previous_prefix = sorted_prefixes[rank - 1]
//                     best = max(best, prefix - previous_prefix)
// 
//                 current_rank = bisect_left(sorted_prefixes, prefix) + 1
//                 fenwick.add(current_rank, 1)
// 
//             return best
// 
//         answer = -10**18
// 
//         if row_count <= col_count:
//             for top in range(row_count):
//                 column_sums = [0] * col_count
// 
//                 for bottom in range(top, row_count):
//                     for col in range(col_count):
//                         column_sums[col] += matrix[bottom][col]
// 
//                     answer = max(answer, best_subarray_no_larger_than(column_sums))
//                     if answer == k:
//                         return k
//         else:
//             for left in range(col_count):
//                 row_sums = [0] * row_count
// 
//                 for right in range(left, col_count):
//                     for row in range(row_count):
//                         row_sums[row] += matrix[row][right]
// 
//                     answer = max(answer, best_subarray_no_larger_than(row_sums))
//                     if answer == k:
//                         return k
// 
//         return answer
// # @lc code=end
// 
// 
// if __name__ == "__main__":
//     def brute_force_max_sum_submatrix(matrix: List[List[int]], k: int) -> int:
//         rows = len(matrix)
//         cols = len(matrix[0])
//         best = -10**18
// 
//         prefix = [[0] * (cols + 1) for _ in range(rows + 1)]
//         for row in range(rows):
//             for col in range(cols):
//                 prefix[row + 1][col + 1] = (
//                     matrix[row][col]
//                     + prefix[row][col + 1]
//                     + prefix[row + 1][col]
//                     - prefix[row][col]
//                 )
// 
//         for top in range(rows):
//             for bottom in range(top, rows):
//                 for left in range(cols):
//                     for right in range(left, cols):
//                         rectangle_sum = (
//                             prefix[bottom + 1][right + 1]
//                             - prefix[top][right + 1]
//                             - prefix[bottom + 1][left]
//                             + prefix[top][left]
//                         )
//                         if rectangle_sum <= k:
//                             best = max(best, rectangle_sum)
// 
//         return best
// 
//     solution = Solution()
// 
//     fixed_tests = [
//         ([[1, 0, 1], [0, -2, 3]], 2, 2),
//         ([[2, 2, -1]], 3, 3),
//         ([[-5]], -2, -5),
//         ([[5, -4, 3]], 4, 4),
//         ([[2], [2], [-1]], 3, 3),
//         ([[4, -1], [-2, 3]], 2, 2),
//     ]
// 
//     for test_matrix, test_k, expected in fixed_tests:
//         assert solution.maxSumSubmatrix(test_matrix, test_k) == expected
// 
//     random_cases = [
//         ([[1, -2, 3], [-4, 5, -6]], 4),
//         ([[2, -1], [-3, 4], [1, -2]], 3),
//         ([[-1, -2], [-3, -4]], -3),
//         ([[0, 0, 0], [0, 0, 0]], 0),
//     ]
// 
//     for test_matrix, test_k in random_cases:
//         expected = brute_force_max_sum_submatrix(test_matrix, test_k)
//         assert solution.maxSumSubmatrix(test_matrix, test_k) == expected

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

class FenwickTree {
    int size;
    vector<int> tree;
public:
    FenwickTree(int n) : size(n), tree(n + 1) {}
    void add(int i, int delta) {
        while (i <= size) {
            tree[i] += delta;
            i += i & -i;
        }
    }
    int sum(int i) {
        int total = 0;
        while (i > 0) {
            total += tree[i];
            i -= i & -i;
        }
        return total;
    }
    int findByOrder(int order) {
        int idx = 0;
        int bit = 1;
        while ((bit << 1) <= size) bit <<= 1;
        while (bit) {
            int next = idx + bit;
            if (next <= size && tree[next] < order) {
                idx = next;
                order -= tree[next];
            }
            bit >>= 1;
        }
        return idx + 1;
    }
};

class Solution {
    int bestSubarray(const vector<int>& values, int k) {
        int prefix = 0;
        vector<int> prefixes{0};
        for (int v : values) {
            prefix += v;
            prefixes.push_back(prefix);
        }
        sort(prefixes.begin(), prefixes.end());
        prefixes.erase(unique(prefixes.begin(), prefixes.end()), prefixes.end());
        FenwickTree bit(prefixes.size());
        int best = INT_MIN;
        prefix = 0;
        bit.add(lower_bound(prefixes.begin(), prefixes.end(), 0) - prefixes.begin() + 1, 1);
        for (int v : values) {
            prefix += v;
            int lower = prefix - k;
            int lowerIndex = lower_bound(prefixes.begin(), prefixes.end(), lower) - prefixes.begin();
            int seenBefore = bit.sum(lowerIndex);
            int totalSeen = bit.sum(prefixes.size());
            if (totalSeen > seenBefore) {
                int rank = bit.findByOrder(seenBefore + 1);
                best = max(best, prefix - prefixes[rank - 1]);
            }
            bit.add(lower_bound(prefixes.begin(), prefixes.end(), prefix) - prefixes.begin() + 1, 1);
        }
        return best;
    }

public:
    int maxSumSubmatrix(vector<vector<int>>& matrix, int k) {
        int rows = matrix.size(), cols = matrix[0].size();
        int ans = INT_MIN;
        if (rows <= cols) {
            for (int top = 0; top < rows; ++top) {
                vector<int> sums(cols);
                for (int bottom = top; bottom < rows; ++bottom) {
                    for (int c = 0; c < cols; ++c) sums[c] += matrix[bottom][c];
                    ans = max(ans, bestSubarray(sums, k));
                    if (ans == k) return k;
                }
            }
        } else {
            for (int left = 0; left < cols; ++left) {
                vector<int> sums(rows);
                for (int right = left; right < cols; ++right) {
                    for (int r = 0; r < rows; ++r) sums[r] += matrix[r][right];
                    ans = max(ans, bestSubarray(sums, k));
                    if (ans == k) return k;
                }
            }
        }
        return ans;
    }
};
