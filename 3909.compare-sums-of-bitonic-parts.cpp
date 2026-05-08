// Translated from 3909.compare-sums-of-bitonic-parts.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3909 lang=python3
// #
// # [3909] Compare Sums of Bitonic Parts
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given a bitonic array nums.
// #
// # A bitonic array is strictly increasing up to one peak, then strictly
// # decreasing after that peak.
// #
// # Split it into:
// #   ascending part:  nums[0..peak]
// #   descending part: nums[peak..n-1]
// #
// # The peak belongs to both parts.
// #
// # Return:
// #   0  if ascending sum is greater
// #   1  if descending sum is greater
// #   -1 if both sums are equal
// #
// #
// # Key observation
// # Because nums is guaranteed to be bitonic, the peak is the unique maximum
// # element.
// #
// # So we only need to:
// #   1. find the peak index,
// #   2. sum left part including peak,
// #   3. sum right part including peak,
// #   4. compare.
// #
// # There is no need for dynamic programming or any advanced data structure.
// #
// #
// # Finding the peak
// # The simplest approach is a linear scan:
// #   peak = index of max(nums)
// #
// # Since the array is bitonic, this is exactly the split point.
// #
// # A binary search peak finder is also possible in O(log n), but we still need
// # sums of both parts. Without prefix sums, summing is O(n), so a linear peak scan
// # is perfectly appropriate.
// #
// #
// # Computing the sums
// # If peak = p:
// #
// #   ascending_sum = sum(nums[:p+1])
// #   descending_sum = sum(nums[p:])
// #
// # Notice nums[p] is included in both sums, exactly as the statement requires.
// #
// #
// # Data structure choice
// # We use only integer variables.
// #
// # The input array itself is enough. No auxiliary arrays are needed because there
// # is only one query and one split.
// #
// #
// # Walkthrough of the code
// # 1. Find peak index with max(range(len(nums)), key=nums.__getitem__).
// # 2. Compute ascending sum over nums[0..peak].
// # 3. Compute descending sum over nums[peak..n-1].
// # 4. Compare:
// #      ascending > descending -> return 0
// #      ascending < descending -> return 1
// #      equal                  -> return -1
// #
// #
// # Correctness proof
// #
// # Lemma 1: The maximum element is the peak of the bitonic array.
// # Proof:
// # The array strictly increases up to the peak, so every element before the peak
// # is smaller than it. It strictly decreases after the peak, so every element
// # after the peak is also smaller than it. Therefore the peak is the unique
// # maximum.
// #
// # Lemma 2: The algorithm computes the correct ascending and descending part sums.
// # Proof:
// # By Lemma 1, the found peak index is the split point. The ascending part is
// # exactly nums[0..peak], and the descending part is exactly nums[peak..n-1].
// # The code sums exactly those ranges, including the peak in both.
// #
// # Theorem: The algorithm returns the required comparison value.
// # Proof:
// # By Lemma 2, the two computed sums are the exact sums requested by the problem.
// # The final if/elif/else directly implements the required return convention.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums).
// #
// # Time:
// #   Finding the peak is O(n).
// #   Summing the two parts is O(n).
// #   Overall time complexity: O(n).
// #
// # Space:
// #   Only a few integer variables are used.
// #   Overall space complexity: O(1), ignoring Python slice-free summation.
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Descending part larger:
// #      nums = [1,3,2,1] -> 1
// #
// # 2. Ascending part larger:
// #      nums = [2,4,5,2] -> 0
// #
// # 3. Equal sums:
// #      nums = [1,2,4,3] -> -1
// #
// # 4. Peak near the left:
// #      nums = [5,4,3] -> descending part includes most elements.
// #
// # 5. Peak near the right:
// #      nums = [1,3,5] is not decreasing after peak under the strict two-sided
// #      definition, but if the platform allows peak at the end, the same summing
// #      logic still works.
// #
// #
// # Edge cases
// #
// # - n is at least 3.
// # - Values can be large, so sums can be up to about 1e14; Python handles this.
// # - Peak is counted twice intentionally.
// #
// #
// # Possible improvements
// #
// # - Binary search can find the peak in O(log n), but total time remains O(n) if
// #   we still compute sums directly.
// # - Prefix sums would help only if there were many queries. For one comparison,
// #   direct summation is simpler.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// class Solution:
//     def compareBitonicSums(self, nums: list[int]) -> int:
//         peak = max(range(len(nums)), key=nums.__getitem__)
// 
//         ascending_sum = 0
//         for i in range(peak + 1):
//             ascending_sum += nums[i]
// 
//         descending_sum = 0
//         for i in range(peak, len(nums)):
//             descending_sum += nums[i]
// 
//         if ascending_sum > descending_sum:
//             return 0
//         if descending_sum > ascending_sum:
//             return 1
//         return -1
// 
// 
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
    int compareBitonicSums(vector<int>& nums) {
        int peak = max_element(nums.begin(), nums.end()) - nums.begin();
        long long asc = 0, desc = 0;
        for (int i = 0; i <= peak; ++i) asc += nums[i];
        for (int i = peak; i < (int)nums.size(); ++i) desc += nums[i];
        if (asc > desc) return 0;
        if (desc > asc) return 1;
        return -1;
    }
};
