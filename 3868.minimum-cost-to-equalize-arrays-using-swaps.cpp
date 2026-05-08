// Translated from 3868.minimum-cost-to-equalize-arrays-using-swaps.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3868 lang=python3
// #
// # [3868] Minimum Cost to Equalize Arrays Using Swaps
// #
// # https://leetcode.com/problems/minimum-cost-to-equalize-arrays-using-swaps/description/
// #
// # algorithms
// # Medium (48.48%)
// # Likes:    66
// # Dislikes: 2
// # Total Accepted:    24.7K
// # Total Submissions: 50.9K
// # Testcase Example:  '[10,20]\n[20,10]'
// #
// # You are given two integer arrays nums1 and nums2 of size n.
// # 
// # You can perform the following two operations any number of times on these two
// # arrays:
// # 
// # 
// # Swap within the same array: Choose two indices i and j. Then, choose either
// # to swap nums1[i] and nums1[j], or nums2[i] and nums2[j]. This operation is
// # free of charge.
// # Swap between two arrays: Choose an index i. Then, swap nums1[i] and nums2[i].
// # This operation incurs a cost of 1.
// # 
// # 
// # Return an integer denoting the minimum cost to make nums1 and nums2
// # identical. If this is not possible, return -1.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: nums1 = [10,20], nums2 = [20,10]
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # 
// # Swap nums2[0] = 20 and nums2[1] = 10.
// # 
// # 
// # nums2 becomes [10, 20].
// # This operation is free of charge.
// # 
// # 
// # nums1 and nums2 are now identical. The cost is 0.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums1 = [10,10], nums2 = [20,20]
// # 
// # Output: 1
// # 
// # Explanation:
// # 
// # 
// # Swap nums1[0] = 10 and nums2[0] = 20.
// # 
// # 
// # nums1 becomes [20, 10].
// # nums2 becomes [10, 20].
// # This operation costs 1.
// # 
// # 
// # Swap nums2[0] = 10 and nums2[1] = 20.
// # 
// # nums2 becomes [20, 10].
// # This operation is free of charge.
// # 
// # 
// # nums1 and nums2 are now identical. The cost is 1.
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: nums1 = [10,20], nums2 = [30,40]
// # 
// # Output: -1
// # 
// # Explanation:
// # 
// # It is impossible to make the two arrays identical. Therefore, the answer is
// # -1.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 2 <= n == nums1.length == nums2.length <= 8 * 10^4
// # 1 <= nums1[i], nums2[i] <= 8 * 10^4
// # 
// # 
// #
// 
// # @lc code=start
// from collections import Counter
// 
// 
// class Solution:
//     def minCost(self, nums1: list[int], nums2: list[int]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We have two arrays of the same length.
// 
//         Operations:
// 
//         * Swap two elements inside `nums1`, or inside `nums2`.
//           This is free.
// 
//         * Swap `nums1[i]` with `nums2[i]` at the same index.
//           This costs 1.
// 
//         We need the minimum paid cost to make the two arrays identical.
// 
//         Key observation: order does not matter
//         --------------------------------------
//         Since swaps inside the same array are free, we can rearrange each array
//         however we want at no cost.
// 
//         Therefore, the real question is not whether the arrays can be made equal
//         index-by-index immediately.  The question is:
// 
//             Can we make the multisets of values in nums1 and nums2 equal?
// 
//         Once the two arrays have the same multiset, free internal swaps can order
//         them identically.
// 
//         Feasibility condition
//         ---------------------
//         For every value `x`, suppose it appears:
// 
//             count1[x] times in nums1
//             count2[x] times in nums2
// 
//         In the final state, both arrays must contain the same number of `x`.
//         Since the total number of copies of `x` across both arrays is:
// 
//             total[x] = count1[x] + count2[x]
// 
//         each array must end with:
// 
//             total[x] / 2
// 
//         copies of `x`.
// 
//         Therefore, `total[x]` must be even for every value.  If any value has an
//         odd total count, it is impossible.
// 
//         How many paid swaps are needed?
//         -------------------------------
//         If a value appears too many times in `nums1`, those extra copies must be
//         moved to `nums2`.  If a value appears too many times in `nums2`, those
//         extra copies must be moved to `nums1`.
// 
//         For value `x`, the number of extra copies in `nums1` is:
// 
//             surplus_in_nums1[x] = count1[x] - total[x] / 2
// 
//         If this is positive, that many copies must leave `nums1`.
// 
//         A paid cross-array swap can fix one surplus copy from each side:
// 
//         * one value that nums1 has too many of moves to nums2
//         * one value that nums2 has too many of moves to nums1
// 
//         Because internal rearrangement is free, we can always place those two
//         surplus values at the same index before performing the paid swap.
// 
//         Thus the minimum cost is:
// 
//             sum of all positive surplus values in nums1
// 
//         This is also equal to the number of surplus items in nums2, because both
//         arrays have the same length.
// 
//         Example
//         -------
//         nums1 = [10, 10]
//         nums2 = [20, 20]
// 
//         Total counts:
// 
//             10 appears 2 times total, so each array needs one 10.
//             20 appears 2 times total, so each array needs one 20.
// 
//         nums1 has one extra 10.
//         nums2 has one extra 20.
// 
//         One paid swap exchanges them, so answer = 1.
// 
//         Data structure choice
//         ---------------------
//         We use `Counter` to count frequencies in both arrays.
// 
//         This is ideal because:
// 
//         * values can be up to 80,000, but only values that appear matter
//         * frequency lookup/update is O(1) average time
//         * the code directly matches the multiset reasoning
// 
//         Algorithm
//         ---------
//         1. Count values in both arrays:
// 
//                count1 = Counter(nums1)
//                count2 = Counter(nums2)
// 
//         2. For every value appearing in either array:
//               - compute `total = count1[value] + count2[value]`
//               - if `total` is odd, return -1
//               - desired copies per array = total // 2
//               - if nums1 has more than desired, add the surplus to the answer
// 
//         3. Return the answer.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: If any value has odd total frequency across both arrays, making
//         the arrays identical is impossible.
//         In the final state, identical arrays must contain the same number of that
//         value.  Therefore the total number of copies must split equally between
//         the two arrays.  An odd total cannot be split into two equal integers.
// 
//         Lemma 2: If every value has even total frequency, the target multiset for
//         each array is uniquely determined.
//         For each value `x`, both arrays must contain exactly
//         `(count1[x] + count2[x]) // 2` copies.  There is no other possible final
//         equal multiset.
// 
//         Lemma 3: At least `sum(max(0, count1[x] - target[x]))` paid swaps are
//         necessary.
//         Every positive surplus copy in `nums1` must leave `nums1`, and the only
//         operation that moves an element between arrays is the paid same-index
//         swap.  Each paid swap moves only one element out of `nums1`, so at least
//         that many paid swaps are required.
// 
//         Lemma 4: That many paid swaps are sufficient.
//         Pair each surplus item in `nums1` with one surplus item in `nums2`.
//         The number of surplus items on both sides is equal because both arrays
//         have the same length and every value has a balanced target count.  Before
//         each paid swap, use free internal swaps to place the paired surplus items
//         at the same index, then swap between arrays.  This reduces both
//         surpluses by one.  Repeating this achieves the target multisets.
// 
//         Theorem: The algorithm returns the minimum possible cost.
//         If the algorithm returns -1, Lemma 1 says the task is impossible.  If it
//         returns a number, Lemma 3 proves no smaller cost can work, and Lemma 4
//         proves that exact cost is achievable.  Therefore the returned cost is
//         optimal.
// 
//         Complexity analysis
//         -------------------
//         Let n be the array length, and let u be the number of distinct values
//         across both arrays.
// 
//         Counting both arrays costs O(n).  Scanning all distinct values costs
//         O(u), and u <= 2n.
// 
//         Total time:  O(n)
//         Total space: O(u), at most O(n)
// 
//         Edge cases
//         ----------
//         * Arrays already have the same multiset:
//           The surplus is 0, so answer is 0.
// 
//         * A value has odd total count:
//           Return -1 immediately.
// 
//         * All values in nums1 must be exchanged with values in nums2:
//           The answer is the number of surplus elements in nums1.
// 
//         * Duplicate values:
//           Counts handle duplicates naturally.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [10,20], [20,10] -> 0
//               [10,10], [20,20] -> 1
//               [10,20], [30,40] -> -1
// 
//         * Already identical arrays.
//         * Arrays with same multiset but different order.
//         * Impossible odd-total frequencies.
//         * Random small arrays checked against brute-force multiset balancing.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal.  We must read the arrays, so O(n) time is the
//         best possible.  The frequency map is the natural minimal information
//         needed to solve the problem.
//         """
// 
//         count1 = Counter(nums1)
//         count2 = Counter(nums2)
// 
//         cost = 0
//         for value in count1.keys() | count2.keys():
//             total = count1[value] + count2[value]
//             if total % 2:
//                 return -1
// 
//             target = total // 2
//             if count1[value] > target:
//                 cost += count1[value] - target
// 
//         return cost
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
    int minCost(vector<int>& nums1, vector<int>& nums2) {
        unordered_map<int, int> c1, c2;
        for (int x : nums1) ++c1[x];
        for (int x : nums2) ++c2[x];
        unordered_set<int> keys;
        for (auto [x, _] : c1) keys.insert(x);
        for (auto [x, _] : c2) keys.insert(x);
        int cost = 0;
        for (int x : keys) {
            int total = c1[x] + c2[x];
            if (total % 2) return -1;
            int target = total / 2;
            if (c1[x] > target) cost += c1[x] - target;
        }
        return cost;
    }
};
