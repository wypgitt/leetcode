// Translated from 3865.reverse-k-subarrays.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3865 lang=python3
// #
// # [3865] Reverse K Subarrays
// #
// # https://leetcode.com/problems/reverse-k-subarrays/description/
// #
// # algorithms
// # Medium (89.32%)
// # Likes:    4
// # Dislikes: 2
// # Total Accepted:    702
// # Total Submissions: 785
// # Testcase Example:  '[1,2,4,3,5,6]\n3'
// #
// # You are given an integer array nums of length n and an integer k.
// # 
// # You must partition the array into k contiguous subarrays of equal length and
// # reverse each subarray.
// # 
// # It is guaranteed that n is divisible by k.
// # 
// # Return the resulting array after performing the above operation.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: nums = [1,2,4,3,5,6], k = 3
// # 
// # Output: [2,1,3,4,6,5]
// # 
// # Explanation:
// # 
// # 
// # The array is partitioned into k = 3 subarrays: [1, 2], [4, 3], and [5,
// # 6].
// # After reversing each subarray: [2, 1], [3, 4], and [6, 5].
// # Combining them gives the final array [2, 1, 3, 4, 6, 5].
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums = [5,4,4,2], k = 1
// # 
// # Output: [2,4,4,5]
// # 
// # Explanation:
// # 
// # 
// # The array is partitioned into k = 1 subarray: [5, 4, 4, 2].
// # Reversing it produces [2, 4, 4, 5], which is the final array.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n == nums.length <= 1000
// # 1 <= nums[i] <= 1000
// # 1 <= k <= n
// # n is divisible by k.
// # 
// # 
// #
// 
// # @lc code=start
// class Solution:
//     def reverseSubarrays(self, nums: list[int], k: int) -> list[int]:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given an array `nums` of length `n` and an integer `k`.
// 
//         We must:
// 
//         1. Partition `nums` into exactly `k` contiguous subarrays.
//         2. Every subarray must have equal length.
//         3. Reverse each subarray.
//         4. Return the final concatenated array.
// 
//         The problem guarantees:
// 
//             n is divisible by k
// 
//         so the partition is always possible.
// 
//         Important detail
//         ----------------
//         Here, `k` is the number of subarrays, not the size of each subarray.
// 
//         Therefore:
// 
//             block_length = n // k
// 
//         Example:
// 
//             nums = [1,2,4,3,5,6]
//             k = 3
// 
//             n = 6
//             block_length = 6 // 3 = 2
// 
//             blocks:
//                 [1,2], [4,3], [5,6]
// 
//         Algorithm
//         ---------
//         1. Compute `block_length = len(nums) // k`.
//         2. Create an empty result array.
//         3. Walk through the input by blocks:
// 
//                start = 0, block_length, 2 * block_length, ...
// 
//         4. For each block `nums[start : start + block_length]`, append its
//            reversed order to the result.
//         5. Return the result.
// 
//         Data structure choice
//         ---------------------
//         We build a result list because the problem asks us to return the
//         resulting array.  Python slicing makes the implementation concise:
// 
//             nums[start:end][::-1]
// 
//         This creates the current block and reverses it.  Since `n <= 1000`, this
//         is easily efficient enough and very readable.
// 
//         If we wanted to avoid temporary block slices, we could append elements
//         manually from `end - 1` down to `start`, but the asymptotic complexity is
//         the same.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: The algorithm partitions the array into exactly `k` contiguous
//         equal-length blocks.
//         Since `block_length = n // k` and `n` is divisible by `k`, the starts
//         `0, block_length, 2 * block_length, ...` cover the array with exactly
//         `k` non-overlapping contiguous blocks, each of length `block_length`.
// 
//         Lemma 2: For every block, the algorithm appends exactly that block in
//         reversed order.
//         For a block `nums[start:end]`, Python's `[::-1]` slice produces the same
//         elements in reverse order.  The algorithm extends the answer with that
//         reversed slice.
// 
//         Lemma 3: The final result preserves the required block order.
//         The algorithm processes blocks from left to right and appends each
//         reversed block immediately.  Therefore the reversed first block appears
//         first, then the reversed second block, and so on.
// 
//         Theorem: The algorithm returns exactly the array required by the
//         problem.
//         By Lemma 1, the partition is the required equal-length partition.  By
//         Lemma 2, each partition block is reversed.  By Lemma 3, the reversed
//         blocks are concatenated in the original block order.  This is exactly the
//         specified operation.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(nums).
// 
//         Every element is copied into the result exactly once.
// 
//         Total time:  O(n)
//         Total space: O(n)
// 
//         The output array itself requires O(n) space.  Temporary slices also take
//         space proportional to one block at a time.
// 
//         Edge cases
//         ----------
//         * k = 1:
//           There is one block: the whole array.  The result is `nums` reversed.
// 
//         * k = n:
//           Every block has length 1.  Reversing length-1 blocks changes nothing.
// 
//         * n = 1:
//           The only valid k is 1, and the result is the same single element.
// 
//         * Duplicate values:
//           Values are copied by position; duplicates do not need special logic.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [1,2,4,3,5,6], k = 3 -> [2,1,3,4,6,5]
//               [5,4,4,2],     k = 1 -> [2,4,4,5]
// 
//         * k = n:
//               [1,2,3], k = 3 -> [1,2,3]
// 
//         * block length greater than 2:
//               [1,2,3,4,5,6], k = 2 -> [3,2,1,6,5,4]
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal: every element must appear in the output, so
//         O(n) time is required.  An in-place version could use O(1) extra space if
//         mutation were desired, but returning a new list is simple and clear.
//         """
// 
//         block_length = len(nums) // k
//         result: list[int] = []
// 
//         for start in range(0, len(nums), block_length):
//             end = start + block_length
//             result.extend(nums[start:end][::-1])
// 
//         return result
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
    vector<int> reverseSubarrays(vector<int>& nums, int k) {
        int block = nums.size() / k;
        if (block <= 0) return {};
        vector<int> res;
        for (int start = 0; start < (int)nums.size(); start += block) {
            int end = min((int)nums.size(), start + block);
            for (int i = end - 1; i >= start; --i) res.push_back(nums[i]);
        }
        return res;
    }
};
