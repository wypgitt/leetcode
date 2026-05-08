// Translated from 3806.maximum-bitwise-and-after-increment-operations.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3806 lang=python3
// #
// # [3806] Maximum Bitwise AND After Increment Operations
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given nums, k, and m.
// #
// # We may perform at most k operations. Each operation increments one nums[i] by 1.
// #
// # After the increments, choose any subset of size m. Return the maximum possible
// # bitwise AND of the chosen m values.
// #
// # Example:
// #   nums = [3, 1, 2], k = 8, m = 2
// #   We can make 3 -> 6 and 2 -> 6 using 7 total increments.
// #   Chosen values [6, 6] have AND 6.
// #
// #
// # Key observation: test a target AND mask
// # Suppose we want the final AND to contain all bits in mask.
// #
// # For a chosen number x, it does not need to equal mask. It only needs:
// #   final_value & mask == mask
// #
// # because every chosen number must contain every 1-bit of mask.
// #
// # So the feasibility question is:
// #
// #   Can we pick at least m numbers and increment them so that each contains all
// #   bits of mask, using total cost <= k?
// #
// # For each nums[i], compute:
// #   cost(nums[i], mask) = minimum nonnegative increment d such that
// #                         (nums[i] + d) contains every bit of mask
// #
// # Then mask is feasible iff the sum of the m smallest costs is <= k.
// #
// #
// # Greedy over answer bits
// # Bitwise AND optimization is naturally greedy from high bit to low bit.
// #
// # Start:
// #   answer = 0
// #
// # For bit from high to low:
// #   candidate = answer | (1 << bit)
// #   if candidate is feasible:
// #       answer = candidate
// #
// # This works because keeping a higher bit is always more valuable than any
// # combination of lower bits. The feasibility test is monotonic:
// #   if a mask is feasible, any submask is also feasible.
// #
// #
// # Computing cost(x, mask)
// # We need the smallest y >= x such that:
// #   (y & mask) == mask
// #
// # A naive loop y = x, x+1, x+2... is too slow.
// #
// # Process bits from high to low and repair missing required bits.
// #
// # Let y start as x.
// # For each bit b from high to low:
// #   if mask requires bit b and y does not have bit b:
// #      We must increase y enough to make bit b become 1.
// #
// #      The smallest number greater than current y that has bit b = 1 is:
// #         ((y >> b) + 1) << b
// #
// #      This clears all lower bits. To make the result as small as possible while
// #      also satisfying already/possibly required lower mask bits, set the lower
// #      bits that mask requires:
// #         y |= mask & ((1 << b) - 1)
// #
// # After processing all bits, y is the minimum valid value.
// #
// #
// # Example of cost
// #   x = 9  = 1001b
// #   mask = 6 = 0110b
// #
// # Need bits 2 and 1.
// # Bit 2 is missing in x, so jump to:
// #   ((9 >> 2) + 1) << 2 = (2 + 1) << 2 = 12 = 1100b
// # Set lower required mask bits below bit 2:
// #   lower required bit 1 -> 1110b = 14
// #
// # y = 14 contains mask bits 2 and 1, and no smaller value >= 9 does.
// #
// #
// # Data structures
// # We do not need a complex data structure:
// #   - For every candidate mask, compute costs for all nums.
// #   - Keep the m smallest costs.
// #
// # Since n <= 5 * 10^4 and there are only about 31 bits, sorting all costs for
// # every bit is acceptable:
// #   O(31 * n log n)
// #
// # In the implementation, we optimize a little by sorting and summing the first m.
// # A max-heap of size m could reduce this to O(31 * n log m), but sorting is
// # simpler and fast enough for the constraints.
// #
// #
// # Choosing the highest bit to scan
// # nums[i] <= 1e9 and k <= 1e9, so any final chosen value is at most about 2e9.
// # That is below 2^31. Scanning bits 31 down to 0 is safe and simple.
// #
// #
// # Walkthrough of the code
// # 1. Initialize ans = 0.
// # 2. For bit from 31 down to 0:
// #      candidate = ans | (1 << bit)
// #      if feasible(candidate):
// #          ans = candidate
// # 3. feasible(mask):
// #      - compute cost(x, mask) for every x in nums
// #      - sort costs
// #      - return sum of smallest m costs <= k
// # 4. cost(x, mask):
// #      - greedily repair missing required bits from high to low
// #      - return repaired_value - x
// #
// #
// # Correctness proof
// #
// # Lemma 1: For a fixed mask, choosing the m numbers with smallest individual
// # costs is optimal.
// # Proof:
// # Each chosen number can be adjusted independently. The only shared constraint is
// # the total operation budget. Therefore, to make m numbers satisfy the mask with
// # minimum total cost, we must choose the m smallest per-number costs.
// #
// # Lemma 2: The cost function returns the minimum y - x such that y >= x and
// # (y & mask) == mask.
// # Proof:
// # Process bits from high to low. When a required bit b is already 1 in y, no
// # change is needed. When it is 0, any valid number with the same higher prefix
// # would still have bit b = 0, so we must increase the higher prefix minimally:
// #   ((y >> b) + 1) << b
// # This is the smallest number above y that turns bit b on. Lower bits do not
// # affect higher-order minimality; setting exactly the required lower mask bits
// # gives the smallest possible suffix that can still satisfy future lower
// # requirements. By induction over bits, the final y is minimal.
// #
// # Lemma 3: feasible(mask) is true iff there exists a valid subset of size m whose
// # final AND contains mask.
// # Proof:
// # A final AND contains mask iff every selected value contains all bits of mask.
// # By Lemma 2, cost(x, mask) is the minimum cost to make each individual value
// # satisfy that condition. By Lemma 1, the cheapest subset of size m is the m
// # smallest costs. It is possible exactly when their sum is <= k.
// #
// # Lemma 4: The high-to-low greedy bit construction returns the maximum feasible
// # AND value.
// # Proof:
// # At a given bit, all higher bits have already been decided optimally. If adding
// # this bit is feasible, any answer without it is smaller regardless of lower
// # bits, so we must keep it. If adding it is infeasible, no answer with the fixed
// # higher prefix can contain it, so it must remain 0. This is the standard
// # lexicographic/numeric greedy argument for bitmask maximization.
// #
// # Theorem: The algorithm returns the maximum possible bitwise AND.
// # Proof:
// # By Lemma 3, feasibility tests exactly whether a candidate mask can be achieved
// # by some subset and increments. By Lemma 4, greedily accepting feasible bits
// # from high to low constructs the largest achievable mask, which is the maximum
// # possible AND.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums), and B = 32 scanned bits.
// #
// # cost(x, mask) checks B bits, so one feasibility test is:
// #   O(n * B + n log n)
// #
// # We perform B feasibility tests:
// #   O(B * (n * B + n log n))
// #
// # With B = 32, this is effectively O(n log n).
// #
// # Space:
// #   The costs array uses O(n) space.
// #   Other variables are O(1).
// #   Overall space complexity: O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [3,1,2], k = 8, m = 2 -> 6
// #
// # 2. Example 2:
// #      nums = [1,2,8,4], k = 7, m = 3 -> 4
// #
// # 3. Example 3:
// #      nums = [1,1], k = 3, m = 2 -> 2
// #
// # 4. k = 0:
// #      Answer is the maximum AND among any existing subset of size m.
// #
// # 5. m = 1:
// #      We only need maximize one number after increments, so the answer should
// #      be the maximum achievable individual value under budget.
// #
// # 6. Random brute force:
// #      For small nums and k, enumerate all increment distributions and subsets
// #      to compare with this greedy solution.
// #
// #
// # Edge cases
// #
// # - Some nums already satisfy a mask, so their cost is 0.
// # - Increments can carry bits and turn lower bits off; the cost function handles
// #   this by repairing from high to low.
// # - The selected subset is not fixed in advance. Feasibility always chooses the
// #   cheapest m candidates for the current mask.
// #
// #
// # Possible improvements
// #
// # - Replace sorting with a size-m max heap to make feasibility O(n log m).
// # - Use quickselect/nsmallest to get the m smallest costs, though sorting is
// #   simpler and reliable for n = 5 * 10^4 and B = 32.
// # - Cache costs between masks is difficult because adding a bit can change costs
// #   nonlocally due to carries.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     MAX_BIT = 31
// 
//     def maximumAND(self, nums: List[int], k: int, m: int) -> int:
//         ans = 0
// 
//         for bit in range(self.MAX_BIT, -1, -1):
//             candidate = ans | (1 << bit)
//             if self._can_make(nums, k, m, candidate):
//                 ans = candidate
// 
//         return ans
// 
//     def _can_make(self, nums: List[int], budget: int, count: int, mask: int) -> bool:
//         costs = [self._cost_to_contain(value, mask) for value in nums]
//         costs.sort()
//         return sum(costs[:count]) <= budget
// 
//     def _cost_to_contain(self, value: int, mask: int) -> int:
//         target = value
// 
//         for bit in range(self.MAX_BIT, -1, -1):
//             if (mask >> bit) & 1 and not ((target >> bit) & 1):
//                 target = ((target >> bit) + 1) << bit
//                 target |= mask & ((1 << bit) - 1)
// 
//         return target - value
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
    static constexpr int MAX_BIT = 31;

    long long costToContain(long long value, long long mask) {
        long long target = value;
        for (int bit = MAX_BIT; bit >= 0; --bit) {
            if (((mask >> bit) & 1) && !((target >> bit) & 1)) {
                target = ((target >> bit) + 1) << bit;
                target |= mask & ((1LL << bit) - 1);
            }
        }
        return target - value;
    }

    bool canMake(vector<int>& nums, long long budget, int count, long long mask) {
        vector<long long> costs;
        for (int x : nums) costs.push_back(costToContain(x, mask));
        sort(costs.begin(), costs.end());
        return accumulate(costs.begin(), costs.begin() + count, 0LL) <= budget;
    }

public:
    long long maximumAND(vector<int>& nums, int k, int m) {
        long long ans = 0;
        for (int bit = MAX_BIT; bit >= 0; --bit) {
            long long cand = ans | (1LL << bit);
            if (canMake(nums, k, m, cand)) ans = cand;
        }
        return ans;
    }
};
