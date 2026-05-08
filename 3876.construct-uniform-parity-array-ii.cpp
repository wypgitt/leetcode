// Translated from 3876.construct-uniform-parity-array-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3876 lang=python3
// #
// # [3876] Construct Uniform Parity Array II
// #
// # https://leetcode.com/problems/construct-uniform-parity-array-ii/description/
// #
// # algorithms
// # Medium (49.88%)
// # Likes:    72
// # Dislikes: 7
// # Total Accepted:    37.3K
// # Total Submissions: 74.7K
// # Testcase Example:  '[1,4,7]'
// #
// # You are given an array nums1 of n distinct integers.
// # 
// # You want to construct another array nums2 of length n such that the elements
// # in nums2 are either all odd or all even.
// # 
// # For each index i, you must choose exactly one of the following (in any
// # order):
// # 
// # 
// # nums2[i] = nums1[i]​​​​​​​
// # nums2[i] = nums1[i] - nums1[j], for an index j != i, such that nums1[i] -
// # nums1[j] >= 1
// # 
// # 
// # Return true if it is possible to construct such an array, otherwise return
// # false.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: nums1 = [1,4,7]
// # 
// # Output: true
// # 
// # Explanation:​​​​​​​​​​​​​​
// # 
// # 
// # Set nums2[0] = nums1[0] = 1.
// # Set nums2[1] = nums1[1] - nums1[0] = 4 - 1 = 3.
// # Set nums2[2] = nums1[2] = 7.
// # nums2 = [1, 3, 7], and all elements are odd. Thus, the answer is true.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums1 = [2,3]
// # 
// # Output: false
// # 
// # Explanation:
// # 
// # It is not possible to construct nums2 such that all elements have the same
// # parity. Thus, the answer is false.
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: nums1 = [4,6]
// # 
// # Output: true
// # 
// # Explanation:
// # 
// # 
// # Set nums2[0] = nums1[0] = 4.
// # Set nums2[1] = nums1[1] = 6.
// # nums2 = [4, 6], and all elements are even. Thus, the answer is true.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n == nums1.length <= 10^5
// # 1 <= nums1[i] <= 10^9
// # nums1 consists of distinct integers.
// # 
// # 
// #
// 
// # @lc code=start
// class Solution:
//     def uniformArray(self, nums1: list[int]) -> bool:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         For every index `i`, we must create `nums2[i]` by choosing one of:
// 
//         * keep the value:
//               nums2[i] = nums1[i]
// 
//         * subtract another smaller value:
//               nums2[i] = nums1[i] - nums1[j]
// 
//           where `j != i` and the difference must be positive, so
//           `nums1[j] < nums1[i]`.
// 
//         We need to know whether we can make all values in `nums2` have the same
//         parity: either all odd or all even.
// 
//         Key parity facts
//         ----------------
//         Only parity matters.
// 
//         * Keeping `x` gives parity:
// 
//               x % 2
// 
//         * Subtracting `y` gives parity:
// 
//               (x - y) % 2
// 
//           which is the same as:
// 
//               x % 2 XOR y % 2
// 
//         Therefore:
// 
//         * subtracting an even number keeps the parity of `x`
//         * subtracting an odd number flips the parity of `x`
// 
//         Since keeping `x` is always allowed, every number can always keep its
//         original parity.  The only way to change a number's parity is to
//         subtract a smaller odd number.
// 
//         Can we make everything even?
//         ----------------------------
//         Every odd number would need to become even.  To flip an odd number, it
//         must subtract a smaller odd number.
// 
//         But consider the smallest odd number in the array.  It has no smaller
//         odd number available.  It cannot become even.
// 
//         So:
// 
//             all-even construction is possible if and only if nums1 has no odd
//             numbers.
// 
//         In other words, the original array must already be all even.
// 
//         Can we make everything odd?
//         ---------------------------
//         Every odd number can stay odd.
// 
//         Every even number must flip to odd, so every even number needs some
//         smaller odd number to subtract.
// 
//         If `min_odd` is the smallest odd number and `min_even` is the smallest
//         even number, then:
// 
//         * if `min_odd < min_even`, every even number is larger than `min_odd`,
//           so every even number can subtract `min_odd` and become odd.
//         * if `min_even < min_odd`, then the smallest even number has no smaller
//           odd number, so it cannot become odd.
// 
//         So:
// 
//             all-odd construction is possible if and only if there are no even
//             numbers, or the smallest odd number is smaller than the smallest
//             even number.
// 
//         Final condition
//         ---------------
//         The answer is true if:
// 
//         * all numbers are even, or
//         * all numbers are odd, or
//         * the array is mixed and `min_odd < min_even`
// 
//         This can be written compactly as:
// 
//             if one parity is missing:
//                 return True
//             return min_odd < min_even
// 
//         Data structure choice
//         ---------------------
//         We do not need a set, sorting, or dynamic programming.  We only need:
// 
//         * the smallest odd value
//         * the smallest even value
//         * whether each parity exists
// 
//         These can be computed in one scan using two variables.
// 
//         Algorithm
//         ---------
//         1. Initialize:
// 
//                min_odd = infinity
//                min_even = infinity
// 
//         2. Scan every number:
//               - if odd, update `min_odd`
//               - if even, update `min_even`
// 
//         3. If there are only odds or only evens, return True.
//         4. Otherwise return whether `min_odd < min_even`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: A number can change parity if and only if there exists a smaller
//         odd number in `nums1`.
//         Keeping the number keeps its parity.  Subtracting an even number also
//         keeps its parity.  Subtracting an odd number flips its parity.  The
//         difference must be positive, so the subtracted odd number must be
//         smaller.
// 
//         Lemma 2: If the array contains any odd number, making all values even is
//         impossible.
//         Let `x` be the smallest odd number.  By Lemma 1, `x` would need a
//         smaller odd number to flip to even.  No such number exists, so `x`
//         cannot become even.
// 
//         Lemma 3: If the array is all even, making all values even is possible.
//         Keep every number unchanged.
// 
//         Lemma 4: Making all values odd is possible exactly when every even number
//         has a smaller odd number.
//         Odd numbers can stay unchanged.  By Lemma 1, each even number can become
//         odd exactly when it has a smaller odd number.
// 
//         Lemma 5: In a mixed-parity array, every even number has a smaller odd
//         number exactly when `min_odd < min_even`.
//         If `min_odd < min_even`, then `min_odd` is smaller than every even
//         number, so every even can subtract it.  If `min_odd > min_even`, the
//         smallest even number has no smaller odd number, so it cannot flip.
// 
//         Theorem: The algorithm returns true exactly when a uniform-parity array
//         can be constructed.
//         By Lemma 2 and Lemma 3, all-even construction is possible exactly when
//         there are no odd numbers.  By Lemma 4 and Lemma 5, all-odd construction
//         is possible exactly when there are no even numbers or `min_odd <
//         min_even`.  The algorithm checks precisely these cases, so it is
//         correct.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(nums1).
// 
//         We scan the array once and do O(1) work per element.
// 
//         Total time:  O(n)
//         Total space: O(1)
// 
//         Edge cases
//         ----------
//         * n = 1:
//           A single value is already uniformly odd or uniformly even.
// 
//         * All even:
//           Return true by keeping every value.
// 
//         * All odd:
//           Return true by keeping every value.
// 
//         * Mixed, smallest value is odd:
//           Return true because that smallest odd can flip every even value.
// 
//         * Mixed, smallest value is even:
//           Return false because that smallest even cannot become odd, and the
//           smallest odd cannot become even.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [1, 4, 7] -> true
//               [2, 3]    -> false
//               [4, 6]    -> true
// 
//         * Single values:
//               [1] -> true
//               [2] -> true
// 
//         * Mixed with smallest odd:
//               [1, 2, 4] -> true
// 
//         * Mixed with smallest even:
//               [2, 5, 7] -> false
// 
//         * Random small arrays:
//           Compare this condition with brute-force checking of both target
//           parities.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal.  Any algorithm must inspect the input in the
//         worst case, so O(n) time is the best possible.  Space is O(1).
//         """
// 
//         min_odd = float("inf")
//         min_even = float("inf")
// 
//         for value in nums1:
//             if value % 2:
//                 min_odd = min(min_odd, value)
//             else:
//                 min_even = min(min_even, value)
// 
//         if min_odd == float("inf") or min_even == float("inf"):
//             return True
// 
//         return min_odd < min_even
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
    bool uniformArray(vector<int>& nums1) {
        int minOdd = INT_MAX, minEven = INT_MAX;
        for (int v : nums1) {
            if (v & 1) minOdd = min(minOdd, v);
            else minEven = min(minEven, v);
        }
        if (minOdd == INT_MAX || minEven == INT_MAX) return true;
        return minOdd < minEven;
    }
};
