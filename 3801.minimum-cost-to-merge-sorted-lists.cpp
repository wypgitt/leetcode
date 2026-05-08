// Translated from 3801.minimum-cost-to-merge-sorted-lists.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3801 lang=python3
// #
// # [3801] Minimum Cost to Merge Sorted Lists
// #
// # https://leetcode.com/problems/minimum-cost-to-merge-sorted-lists/description/
// #
// # algorithms
// # Hard (34.53%)
// # Likes:    46
// # Dislikes: 5
// # Total Accepted:    4.2K
// # Total Submissions: 12.1K
// # Testcase Example:  '[[1,3,5],[2,4],[6,7,8]]'
// #
// # You are given a 2D integer array lists, where each lists[i] is a non-empty
// # array of integers sorted in non-decreasing order.
// # 
// # You may repeatedly choose two lists a = lists[i] and b = lists[j], where i !=
// # j, and merge them. The cost to merge a and b is:
// # 
// # len(a) + len(b) + abs(median(a) - median(b)), where len and median denote the
// # list length and median, respectively.
// # 
// # After merging a and b, remove both a and b from lists and insert the new
// # merged sorted list in any position. Repeat merges until only one list
// # remains.
// # 
// # Return an integer denoting the minimum total cost required to merge all lists
// # into one single sorted list.
// # 
// # The median of an array is the middle element after sorting it in
// # non-decreasing order. If the array has an even number of elements, the median
// # is the left middle element.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: lists = [[1,3,5],[2,4],[6,7,8]]
// # 
// # Output: 18
// # 
// # Explanation:
// # 
// # Merge a = [1, 3, 5] and b = [2, 4]:
// # 
// # 
// # len(a) = 3 and len(b) = 2
// # median(a) = 3 and median(b) = 2
// # cost = len(a) + len(b) + abs(median(a) - median(b)) = 3 + 2 + abs(3 - 2) =
// # 6
// # 
// # 
// # So lists becomes [[1, 2, 3, 4, 5], [6, 7, 8]].
// # 
// # Merge a = [1, 2, 3, 4, 5] and b = [6, 7, 8]:
// # 
// # 
// # len(a) = 5 and len(b) = 3
// # median(a) = 3 and median(b) = 7
// # cost = len(a) + len(b) + abs(median(a) - median(b)) = 5 + 3 + abs(3 - 7) =
// # 12
// # 
// # 
// # So lists becomes [[1, 2, 3, 4, 5, 6, 7, 8]], and total cost is 6 + 12 = 18.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: lists = [[1,1,5],[1,4,7,8]]
// # 
// # Output: 10
// # 
// # Explanation:
// # 
// # Merge a = [1, 1, 5] and b = [1, 4, 7, 8]:
// # 
// # 
// # len(a) = 3 and len(b) = 4
// # median(a) = 1 and median(b) = 4
// # cost = len(a) + len(b) + abs(median(a) - median(b)) = 3 + 4 + abs(1 - 4) =
// # 10
// # 
// # 
// # So lists becomes [[1, 1, 1, 4, 5, 7, 8]], and total cost is 10.
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: lists = [[1],[3]]
// # 
// # Output: 4
// # 
// # Explanation:
// # 
// # Merge a = [1] and b = [3]:
// # 
// # 
// # len(a) = 1 and len(b) = 1
// # median(a) = 1 and median(b) = 3
// # cost = len(a) + len(b) + abs(median(a) - median(b)) = 1 + 1 + abs(1 - 3) =
// # 4
// # 
// # 
// # So lists becomes [[1, 3]], and total cost is 4.
// # 
// # 
// # Example 4:
// # 
// # 
// # Input: lists = [[1],[1]]
// # 
// # Output: 2
// # 
// # Explanation:
// # 
// # The total cost is len(a) + len(b) + abs(median(a) - median(b)) = 1 + 1 +
// # abs(1 - 1) = 2.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 2 <= lists.length <= 12
// # 1 <= lists[i].length <= 500
// # -10^9 <= lists[i][j] <= 10^9
// # lists[i] is sorted in non-decreasing order.
// # The sum of lists[i].length will not exceed 2000.
// # 
// # 
// #
// 
// # @lc code=start
// from bisect import bisect_right
// from typing import List
// 
// 
// class Solution:
//     def minMergeCost(self, lists: List[List[int]]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given several sorted lists.  In one operation, we choose two
//         current lists `a` and `b`, merge them into one sorted list, and pay:
// 
//             len(a) + len(b) + abs(median(a) - median(b))
// 
//         The median is the left middle element for even-length lists.
// 
//         We must keep merging until one list remains and return the minimum
//         possible total cost.
// 
//         Why this is not a greedy heap problem
//         -------------------------------------
//         If the cost were only:
// 
//             len(a) + len(b)
// 
//         then this would be exactly Huffman merging, and always merging the two
//         shortest lists would be optimal.
// 
//         Here, the extra median distance term:
// 
//             abs(median(a) - median(b))
// 
//         changes after merges because the median of a merged group depends on all
//         values inside that group.  A locally cheap merge can create a group whose
//         median is expensive to merge later.  Therefore a simple greedy strategy
//         is not reliable.
// 
//         Key observation
//         ---------------
//         The number of original lists is small:
// 
//             lists.length <= 12
// 
//         That suggests dynamic programming over subsets.
// 
//         Once some subset of original lists has been merged into one list, two
//         facts are independent of the order used inside that subset:
// 
//         * its length is the total number of elements in those lists
//         * its median is the median of the sorted union of those lists
// 
//         So for every subset mask, we can define:
// 
//             length[mask] = total length of all lists in mask
//             median[mask] = median of all values in lists in mask
// 
//         Then the DP can decide the last merge.
// 
//         DP definition
//         -------------
//         Let:
// 
//             dp[mask] = minimum cost to merge exactly the original lists whose
//                        bits are set in `mask` into one sorted list
// 
//         Base case:
// 
//             dp[single_list_mask] = 0
// 
//         because one list is already one merged list.
// 
//         Transition
//         ----------
//         Suppose the final merge for `mask` combines two non-empty disjoint
//         groups:
// 
//             left
//             right = mask without left
// 
//         Then:
// 
//             cost =
//                 dp[left]
//                 + dp[right]
//                 + length[mask]
//                 + abs(median[left] - median[right])
// 
//         Why `length[mask]`?
//         The final merge merges all elements in `left` and all elements in
//         `right`, so:
// 
//             len(left_merged_list) + len(right_merged_list)
//           = length[left] + length[right]
//           = length[mask]
// 
//         We try every partition and take the minimum.
// 
//         Data structure choice
//         ---------------------
//         1. Bitmask:
//            Since there are at most 12 lists, a subset fits naturally in an
//            integer mask.  This makes subset enumeration compact and efficient.
// 
//         2. Array DP indexed by mask:
//            There are only `2^n` masks, so arrays are simpler and faster than
//            dictionaries.
// 
//         3. Binary search over values for subset medians:
//            The median is the smallest value whose count of elements less than
//            or equal to it reaches the median rank.  Because every original list
//            is sorted, we can precompute:
// 
//                count_leq[list_index][value_index]
// 
//            where `value_index` points into all distinct values from all lists.
//            Then a subset count is just the sum of those counts for the lists in
//            the subset.
// 
//         Precomputing subset medians
//         ---------------------------
//         First collect all distinct values:
// 
//             values = sorted(all values from all lists)
// 
//         For each original list and each candidate value, use `bisect_right` to
//         count how many elements in that list are <= candidate.
// 
//         For each subset mask:
// 
//         1. Its left-middle median rank is:
// 
//                target = (length[mask] - 1) // 2 + 1
// 
//            This is one-based: the first element has rank 1.
// 
//         2. Binary search `values` for the smallest candidate where the subset
//            has at least `target` elements <= candidate.
// 
//         That candidate is exactly the subset median.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For any subset `mask`, `length[mask]` and `median[mask]` depend
//         only on which original lists are in `mask`, not on merge order.
//         Merging sorted lists does not change the multiset of elements.  The
//         final sorted list for a subset is always the sorted union of those
//         original elements.  Therefore its length and median are fixed.
// 
//         Lemma 2: The median precomputation returns the correct median for every
//         subset.
//         For a candidate value `x`, summing the precomputed `count <= x` values
//         over all lists in the subset gives the number of subset elements no
//         larger than `x`.  The median is the smallest value whose count reaches
//         the left-middle rank.  The binary search finds exactly that value.
// 
//         Lemma 3: For every `mask`, the DP transition considers every possible
//         final merge that can produce `mask`.
//         The final operation must merge two non-empty disjoint groups whose union
//         is `mask`.  Enumerating all non-empty proper submasks gives every such
//         split as `(left, mask ^ left)`.
// 
//         Lemma 4: `dp[mask]` is the minimum cost to merge the lists in `mask`.
//         For a singleton mask, the cost is 0, which is correct.  For larger masks,
//         consider an optimal merge plan.  Its final merge splits `mask` into
//         `left` and `right`.  By optimal substructure, the cost before that final
//         merge must be at least `dp[left] + dp[right]`; otherwise we could replace
//         it with a cheaper subplan.  By Lemma 1, the final merge cost is exactly
//         `length[mask] + abs(median[left] - median[right])`.  The transition
//         checks this split and every other split, so it obtains the optimal cost.
// 
//         Theorem: The algorithm returns the minimum total cost to merge all
//         lists.
//         The full set of lists is represented by `full_mask`.  By Lemma 4,
//         `dp[full_mask]` is exactly the minimum cost for that full set.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             n = number of lists, n <= 12
//             T = total number of elements, T <= 2000
//             M = 2^n
// 
//         Median precomputation:
// 
//         Let D be the number of distinct values, so D <= T.
//         Building the per-list count table costs:
// 
//             O(n * D * log T)
// 
//         Then each subset median binary search costs O(n log D), so all subset
//         medians cost:
// 
//             O(M * n * log D)
// 
//         DP transitions:
// 
//         Across all masks, enumerating all submasks costs O(3^n).  We skip
//         duplicate mirror splits, but the asymptotic bound is still:
// 
//             O(3^n)
// 
//         Total time:
// 
//             O(n * D * log T + 2^n * n * log D + 3^n)
// 
//         Space:
// 
//             O(2^n)
// 
//         for the `length`, `median`, `dp`, subset member, and count tables.
// 
//         Edge cases
//         ----------
//         * Exactly two lists:
//           Only one merge is possible.
// 
//         * Lists with duplicate values:
//           The heap handles duplicates naturally; medians can be equal, making
//           the absolute median difference zero.
// 
//         * Negative values:
//           Sorting and absolute differences work the same way.
// 
//         * Even merged length:
//           We use `(length - 1) // 2`, which selects the left middle element as
//           required.
// 
//         * Many possible optimal answers:
//           The problem asks only for the minimum cost, not the merge sequence.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [[1,3,5],[2,4],[6,7,8]] -> 18
//               [[1,1,5],[1,4,7,8]]     -> 10
//               [[1],[3]]               -> 4
//               [[1],[1]]               -> 2
// 
//         * Negative values.
//         * Duplicate medians.
//         * Even total lengths to verify left-middle median.
//         * Small random cases compared with brute force recursion.
// 
//         Possible improvement
//         --------------------
//         Storing the fully merged sorted array for every subset also makes median
//         lookup easy, but it stores millions of references in the worst case.
//         The binary-search count approach is both faster than repeated heap
//         merging and lighter on memory.
//         """
// 
//         list_count = len(lists)
//         mask_count = 1 << list_count
// 
//         lengths = [0] * mask_count
//         medians = [0] * mask_count
//         members = [()] * mask_count
// 
//         for mask in range(1, mask_count):
//             lowest_bit = mask & -mask
//             list_index = lowest_bit.bit_length() - 1
//             previous_mask = mask ^ lowest_bit
//             lengths[mask] = lengths[previous_mask] + len(lists[list_index])
//             members[mask] = members[previous_mask] + (list_index,)
// 
//         distinct_values = sorted({value for values in lists for value in values})
//         count_leq = [
//             [bisect_right(values, candidate) for candidate in distinct_values]
//             for values in lists
//         ]
// 
//         def find_subset_median(mask: int) -> int:
//             target = (lengths[mask] - 1) // 2 + 1
//             left = 0
//             right = len(distinct_values) - 1
//             mask_members = members[mask]
// 
//             while left < right:
//                 middle = (left + right) // 2
//                 count = 0
// 
//                 for list_index in mask_members:
//                     count += count_leq[list_index][middle]
// 
//                 if count >= target:
//                     right = middle
//                 else:
//                     left = middle + 1
// 
//             return distinct_values[left]
// 
//         for mask in range(1, mask_count):
//             medians[mask] = find_subset_median(mask)
// 
//         infinity = 10**30
//         dp = [infinity] * mask_count
// 
//         for i in range(list_count):
//             dp[1 << i] = 0
// 
//         for mask in range(1, mask_count):
//             if mask & (mask - 1) == 0:
//                 continue
// 
//             best = infinity
//             total_length = lengths[mask]
//             submask = (mask - 1) & mask
// 
//             while submask:
//                 other = mask ^ submask
// 
//                 if submask < other:
//                     candidate = (
//                         dp[submask]
//                         + dp[other]
//                         + total_length
//                         + abs(medians[submask] - medians[other])
//                     )
//                     if candidate < best:
//                         best = candidate
// 
//                 submask = (submask - 1) & mask
// 
//             dp[mask] = best
// 
//         return dp[mask_count - 1]
// # @lc code=end
// 
// 
// if __name__ == "__main__":
//     from functools import lru_cache
// 
//     def merged_median(selected_lists: List[List[int]]) -> int:
//         merged = sorted(value for values in selected_lists for value in values)
//         return merged[(len(merged) - 1) // 2]
// 
//     def brute_force_min_merge_cost(test_lists: List[List[int]]) -> int:
//         @lru_cache(None)
//         def solve(state: tuple[tuple[int, ...], ...]) -> int:
//             if len(state) == 1:
//                 return 0
// 
//             best = 10**30
//             state_lists = [list(values) for values in state]
// 
//             for i in range(len(state_lists)):
//                 for j in range(i + 1, len(state_lists)):
//                     first = state_lists[i]
//                     second = state_lists[j]
//                     merged = tuple(sorted(first + second))
//                     cost = (
//                         len(first)
//                         + len(second)
//                         + abs(merged_median([first]) - merged_median([second]))
//                     )
// 
//                     next_state = [
//                         tuple(state_lists[index])
//                         for index in range(len(state_lists))
//                         if index != i and index != j
//                     ]
//                     next_state.append(merged)
//                     next_state.sort()
// 
//                     best = min(best, cost + solve(tuple(next_state)))
// 
//             return best
// 
//         initial_state = tuple(sorted(tuple(values) for values in test_lists))
//         return solve(initial_state)
// 
//     solution = Solution()
// 
//     fixed_tests = [
//         ([[1, 3, 5], [2, 4], [6, 7, 8]], 18),
//         ([[1, 1, 5], [1, 4, 7, 8]], 10),
//         ([[1], [3]], 4),
//         ([[1], [1]], 2),
//         ([[-5, -1], [-3], [10]], 21),
//         ([[1, 10], [2, 9], [3, 8]], 12),
//     ]
// 
//     for test_lists, expected in fixed_tests:
//         assert solution.minMergeCost([values[:] for values in test_lists]) == expected
// 
//     brute_force_cases = [
//         [[1], [2], [3]],
//         [[1, 4], [2], [3, 5]],
//         [[-2, 7], [-1, 0], [3]],
//         [[1, 1], [1, 1], [2]],
//     ]
// 
//     for test_lists in brute_force_cases:
//         expected = brute_force_min_merge_cost(test_lists)
//         assert solution.minMergeCost([values[:] for values in test_lists]) == expected

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
    long long minMergeCost(vector<vector<int>>& lists) {
        int m = lists.size();
        int masks = 1 << m;
        vector<int> len(masks), median(masks);
        vector<vector<int>> members(masks);
        for (int mask = 1; mask < masks; ++mask) {
            int bit = mask & -mask;
            int idx = __builtin_ctz(bit);
            int prev = mask ^ bit;
            len[mask] = len[prev] + lists[idx].size();
            members[mask] = members[prev];
            members[mask].push_back(idx);
        }
        vector<int> values;
        for (auto& v : lists) values.insert(values.end(), v.begin(), v.end());
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        vector<vector<int>> countLeq(m, vector<int>(values.size()));
        for (int i = 0; i < m; ++i) for (int j = 0; j < (int)values.size(); ++j) {
            countLeq[i][j] = upper_bound(lists[i].begin(), lists[i].end(), values[j]) - lists[i].begin();
        }
        auto subsetMedian = [&](int mask) {
            int target = (len[mask] - 1) / 2 + 1;
            int l = 0, r = (int)values.size() - 1;
            while (l < r) {
                int mid = (l + r) / 2, cnt = 0;
                for (int idx : members[mask]) cnt += countLeq[idx][mid];
                if (cnt >= target) r = mid;
                else l = mid + 1;
            }
            return values[l];
        };
        for (int mask = 1; mask < masks; ++mask) median[mask] = subsetMedian(mask);
        const long long INF = (long long)4e18;
        vector<long long> dp(masks, INF);
        for (int i = 0; i < m; ++i) dp[1 << i] = 0;
        for (int mask = 1; mask < masks; ++mask) {
            if ((mask & (mask - 1)) == 0) continue;
            for (int sub = (mask - 1) & mask; sub; sub = (sub - 1) & mask) {
                int other = mask ^ sub;
                if (sub < other) dp[mask] = min(dp[mask], dp[sub] + dp[other] + len[mask] + llabs(median[sub] - median[other]));
            }
        }
        return dp[masks - 1];
    }
};
