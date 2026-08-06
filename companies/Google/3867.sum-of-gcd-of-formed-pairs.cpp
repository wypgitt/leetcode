/*
 * @lc app=leetcode id=3867 lang=cpp
 *
 * [3867] Sum of GCD of Formed Pairs
 */
// Translated from 3867.sum-of-gcd-of-formed-pairs.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3867 lang=python3
// #
// # [3867] Sum of GCD of Formed Pairs
// #
// # https://leetcode.com/problems/sum-of-gcd-of-formed-pairs/description/
// #
// # algorithms
// # Medium (65.72%)
// # Likes:    31
// # Dislikes: 9
// # Total Accepted:    30.9K
// # Total Submissions: 47.1K
// # Testcase Example:  '[2,6,4]'
// #
// # You are given an integer array nums of length n.
// # 
// # Construct an array prefixGcd where for each index i:
// # 
// # 
// # Let mxi = max(nums[0], nums[1], ..., nums[i]).
// # prefixGcd[i] = gcd(nums[i], mxi).
// # 
// # 
// # After constructing prefixGcd:
// # 
// # 
// # Sort prefixGcd in non-decreasing order.
// # Form pairs by taking the smallest unpaired element and the largest unpaired
// # element.
// # Repeat this process until no more pairs can be formed.
// # For each formed pair, compute the gcd of the two elements.
// # If n is odd, the middle element in the prefixGcd array remains unpaired and
// # should be ignored.
// # 
// # 
// # Return an integer denoting the sum of the GCD values of all formed pairs.
// # The term gcd(a, b) denotes the greatest common divisor of a and b.
// # 
// # Example 1:
// # 
// # 
// # Input: nums = [2,6,4]
// # 
// # Output: 2
// # 
// # Explanation:
// # 
// # Construct prefixGcd:
// # 
// # 
// # 
// # 
// # i
// # nums[i]
// # mxi
// # prefixGcd[i]
// # 
// # 
// # 
// # 
// # 0
// # 2
// # 2
// # 2
// # 
// # 
// # 1
// # 6
// # 6
// # 6
// # 
// # 
// # 2
// # 4
// # 6
// # 2
// # 
// # 
// # 
// # 
// # prefixGcd = [2, 6, 2]. After sorting, it forms [2, 2, 6].
// # 
// # Pair the smallest and largest elements: gcd(2, 6) = 2. The remaining middle
// # element 2 is ignored. Thus, the sum is 2.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums = [3,6,2,8]
// # 
// # Output: 5
// # 
// # Explanation:
// # 
// # Construct prefixGcd:
// # 
// # 
// # 
// # 
// # i
// # nums[i]
// # mxi
// # prefixGcd[i]
// # 
// # 
// # 
// # 
// # 0
// # 3
// # 3
// # 3
// # 
// # 
// # 1
// # 6
// # 6
// # 6
// # 
// # 
// # 2
// # 2
// # 6
// # 2
// # 
// # 
// # 3
// # 8
// # 8
// # 8
// # 
// # 
// # 
// # 
// # prefixGcd = [3, 6, 2, 8]. After sorting, it forms [2, 3, 6, 8].
// # 
// # Form pairs: gcd(2, 8) = 2 and gcd(3, 6) = 3. Thus, the sum is 2 + 3 = 5.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n == nums.length <= 10^5
// # 1 <= nums[i] <= 10^​​​​​​​9
// # 
// # 
// #
// 
// # lc-original code=start
// from math import gcd
// 
// 
// class Solution:
//     def gcdSum(self, nums: list[int]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given an array `nums`.
// 
//         First, we construct a new array `prefixGcd`:
// 
//             mx_i = max(nums[0], nums[1], ..., nums[i])
//             prefixGcd[i] = gcd(nums[i], mx_i)
// 
//         Then we:
// 
//         1. Sort `prefixGcd` in non-decreasing order.
//         2. Pair the smallest remaining element with the largest remaining
//            element.
//         3. For each pair, add the gcd of the two paired values.
//         4. If one middle value remains because the length is odd, ignore it.
// 
//         We return the sum of those pair gcd values.
// 
//         Key observation
//         ---------------
//         There is no optimization choice after `prefixGcd` is built.
// 
//         The problem explicitly tells us how to pair after sorting:
// 
//             smallest with largest,
//             second-smallest with second-largest,
//             ...
// 
//         So the task is to implement those steps efficiently and correctly.
// 
//         Building prefixGcd
//         ------------------
//         For each index `i`, we need the maximum value seen so far.  We can keep
//         a running maximum:
// 
//             running_max = max(running_max, nums[i])
// 
//         Then:
// 
//             prefixGcd.append(gcd(nums[i], running_max))
// 
//         This avoids recomputing the maximum over `nums[0..i]` from scratch.
// 
//         Pairing after sorting
//         ---------------------
//         Once `prefixGcd` is sorted:
// 
//             values = sorted(prefixGcd)
// 
//         the required pairs are:
// 
//             values[0] with values[n - 1]
//             values[1] with values[n - 2]
//             values[2] with values[n - 3]
//             ...
// 
//         We can use two pointers:
// 
//             left = 0
//             right = n - 1
// 
//         While `left < right`, add:
// 
//             gcd(values[left], values[right])
// 
//         then move inward:
// 
//             left += 1
//             right -= 1
// 
//         If `left == right`, that is the unpaired middle element, so we stop.
// 
//         Data structure choice
//         ---------------------
//         We use a list for `prefixGcd` because:
// 
//         * we need to store all generated values before sorting
//         * Python lists sort efficiently in O(n log n)
//         * two-pointer pairing is natural on a sorted list
// 
//         No heap is needed because all pairs are determined by global sorted
//         order, and no hash map is needed because frequencies alone would not
//         simplify the gcd pairing enough for values up to 10^9.
// 
//         Algorithm
//         ---------
//         1. Initialize:
// 
//                running_max = 0
//                prefix_gcd = []
// 
//         2. For each `value` in `nums`:
//               - update `running_max`
//               - append `gcd(value, running_max)` to `prefix_gcd`
// 
//         3. Sort `prefix_gcd`.
//         4. Use two pointers from both ends to form required pairs.
//         5. Sum `gcd(left_value, right_value)` for each pair.
//         6. Return the sum.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: The first scan constructs `prefixGcd` exactly as defined.
//         At index `i`, `running_max` is updated to the maximum of all values from
//         `nums[0]` through `nums[i]`.  Therefore appending
//         `gcd(nums[i], running_max)` appends exactly the required
//         `prefixGcd[i]`.
// 
//         Lemma 2: After sorting, the two-pointer loop forms exactly the pairs
//         required by the problem.
//         The sorted array's smallest unpaired element is always at the current
//         `left` pointer, and its largest unpaired element is always at the
//         current `right` pointer.  Pairing them and moving both pointers inward
//         exactly repeats the specified process.
// 
//         Lemma 3: The two-pointer loop ignores exactly the middle element when
//         the length is odd.
//         The loop runs only while `left < right`.  If the array length is odd,
//         eventually `left == right`, meaning one middle element remains unpaired.
//         The loop stops and does not add it, as required.
// 
//         Theorem: The algorithm returns the required sum.
//         By Lemma 1, the constructed array is the correct `prefixGcd`.  By
//         Lemma 2 and Lemma 3, the algorithm forms exactly the required pairs and
//         ignores the middle element when needed.  For each formed pair, it adds
//         the pair's gcd.  Therefore the returned sum is exactly the problem's
//         required value.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(nums), and let M = max(nums).
// 
//         Building `prefixGcd`:
// 
//             O(n log M)
// 
//         because each gcd computation costs O(log M).
// 
//         Sorting:
// 
//             O(n log n)
// 
//         Pairing:
// 
//             O(n log M)
// 
//         for up to n/2 gcd computations.
// 
//         Total time:
// 
//             O(n log n + n log M)
// 
//         In typical interview notation, this is dominated by sorting and written
//         as O(n log n), with gcd cost noted separately.
// 
//         Total space:
// 
//             O(n)
// 
//         for the `prefixGcd` list.
// 
//         Edge cases
//         ----------
//         * n = 1:
//           There are no pairs after sorting, so the answer is 0.
// 
//         * Odd n:
//           The middle sorted value is ignored.
// 
//         * Already increasing nums:
//           The running maximum is often the current value, so
//           `gcd(nums[i], running_max)` may equal `nums[i]`.
// 
//         * Values up to 10^9:
//           Python integers and `math.gcd` handle them safely.
// 
//         * Duplicate prefixGcd values:
//           Sorting and two-pointer pairing handle duplicates naturally.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [2,6,4]   -> 2
//               [3,6,2,8] -> 5
// 
//         * Single element:
//               [7] -> 0
// 
//         * All equal:
//               [5,5,5,5] -> gcd pairs sum is 10
// 
//         * Random arrays:
//           Compare this implementation against a direct reference that computes
//           prefix maxima by slicing and then performs the same sort/pair process.
// 
//         Possible improvement?
//         ---------------------
//         This is already the natural solution.  Since the required pairing is
//         based on sorted order, sorting is unavoidable unless value constraints
//         were small enough for counting sort.  Here values can be up to 10^9, so
//         comparison sorting is the right fit.
//         """
// 
//         prefix_gcd: list[int] = []
//         running_max = 0
// 
//         for value in nums:
//             running_max = max(running_max, value)
//             prefix_gcd.append(gcd(value, running_max))
// 
//         prefix_gcd.sort()
// 
//         answer = 0
//         left = 0
//         right = len(prefix_gcd) - 1
// 
//         while left < right:
//             answer += gcd(prefix_gcd[left], prefix_gcd[right])
//             left += 1
//             right -= 1
// 
//         return answer
// # lc-original code=end

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
    long long gcdSum(vector<int>& nums) {
        vector<int> pref;
        int runningMax = 0;
        for (int v : nums) {
            runningMax = max(runningMax, v);
            pref.push_back(std::gcd(v, runningMax));
        }
        sort(pref.begin(), pref.end());
        long long ans = 0;
        for (int l = 0, r = (int)pref.size() - 1; l < r; ++l, --r) ans += std::gcd(pref[l], pref[r]);
        return ans;
    }
};
// @lc code=end
