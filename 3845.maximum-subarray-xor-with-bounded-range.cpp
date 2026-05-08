/*
 * @lc app=leetcode id=3845 lang=cpp
 *
 * [3845] Maximum Subarray XOR with Bounded Range
 */
// Translated from 3845.maximum-subarray-xor-with-bounded-range.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3845 lang=python3
// #
// # [3845] Maximum Subarray XOR with Bounded Range
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given a non-negative integer array nums and an integer k.
// #
// # Choose a contiguous subarray nums[l..r] such that:
// #   max(nums[l..r]) - min(nums[l..r]) <= k
// #
// # The value of the subarray is:
// #   nums[l] XOR nums[l + 1] XOR ... XOR nums[r]
// #
// # Return the maximum possible subarray XOR value.
// #
// # Example:
// #   nums = [5, 4, 5, 6], k = 2
// #   Subarray [4, 5, 6] has max - min = 6 - 4 = 2 and XOR = 7.
// #   Answer = 7.
// #
// #
// # Two independent problems inside the task
// # For every right endpoint r, we need:
// #
// #   1. Know which left endpoints l are valid under the bounded range condition.
// #   2. Among those valid l, maximize XOR(nums[l..r]).
// #
// # We solve the first with a sliding window and monotonic queues.
// # We solve the second with prefix XORs and a binary trie.
// #
// #
// # Part 1: sliding window for the bounded range
// # Maintain a window [left, right] such that:
// #   max(window) - min(window) <= k
// #
// # Use two deques of indices:
// #   max_q: indices with nums values in decreasing order.
// #          max is nums[max_q[0]].
// #
// #   min_q: indices with nums values in increasing order.
// #          min is nums[min_q[0]].
// #
// # When we append nums[right]:
// #   - pop smaller/equal values from the back of max_q,
// #   - pop larger/equal values from the back of min_q,
// #   - append right to both.
// #
// # If the window violates max - min <= k, move left rightward until it becomes
// # valid again, removing left from the queues if it was at the front.
// #
// # Important monotonicity:
// # Once [left, right] is valid, every subarray ending at right whose start s is in
// # [left, right] is also valid. A subarray of a valid window cannot have larger
// # max-min range than the whole window.
// #
// #
// # Part 2: prefix XOR for subarray XOR
// # Define prefix XOR:
// #   pref[0] = 0
// #   pref[i + 1] = nums[0] XOR nums[1] XOR ... XOR nums[i]
// #
// # Then:
// #   XOR(nums[s..right]) = pref[right + 1] XOR pref[s]
// #
// # For fixed right, valid starts are:
// #   s in [left, right]
// #
// # So we need:
// #   maximize pref[right + 1] XOR pref[s] over s in [left, right]
// #
// # This is the classic maximum-XOR-with-a-set query. The set here is dynamic
// # because left moves, so we need insert, delete, and query.
// #
// #
// # Data structure choice: binary trie with counts
// # nums[i] < 2^15, so every prefix XOR also fits in 15 bits.
// #
// # A binary trie stores the eligible prefix XORs pref[s].
// # Operations:
// #   insert(x): add prefix x to the current window's start set.
// #   remove(x): remove prefix x when its start index moves left of the window.
// #   query(x): return max x XOR y among stored y values.
// #
// # Each trie node stores:
// #   child[0], child[1]: indices of child nodes
// #   count: how many inserted values pass through this node
// #
// # The count is what makes deletion safe. If a child exists but count is 0, it is
// # not currently usable.
// #
// # Query logic:
// #   To maximize XOR bit by bit, at each bit try to move to the opposite bit of x.
// #   If that opposite branch has positive count, take it and set this answer bit.
// #   Otherwise take the same-bit branch.
// #
// #
// # Algorithm
// # Keep prefix values pref[0], pref[1], ..., as we scan.
// #
// # For each right:
// #   1. Insert pref[right] into the trie because start s = right is now possible.
// #   2. Add nums[right] to max_q and min_q.
// #   3. While max - min > k:
// #        - remove pref[left] from the trie,
// #        - move left forward,
// #        - drop expired queue fronts.
// #   4. Compute current_prefix = pref[right + 1].
// #   5. Query trie for the best current_prefix XOR pref[s].
// #   6. Update the answer.
// #
// # The trie always contains exactly:
// #   pref[s] for s in [left, right]
// #
// # which are exactly the valid starts for subarrays ending at right.
// #
// #
// # Correctness proof
// #
// # Lemma 1: After the shrinking loop, [left, right] is the smallest-left valid
// # window ending at right.
// # Proof:
// # The monotonic queues always report the current window max and min. The loop
// # increments left while max - min > k, removing expired elements from both queues.
// # It stops only when the condition becomes valid. Since left only moves forward
// # while the window is invalid, all starts before the final left have been ruled
// # out for this right.
// #
// # Lemma 2: For fixed right, every start s in [left, right] forms a valid subarray,
// # and every start s < left is invalid.
// # Proof:
// # By Lemma 1, [left, right] is valid. Any subarray inside it has max no larger
// # than the window max and min no smaller than the window min, so it is also valid.
// # Starts before left were removed while the window was invalid, so they cannot be
// # valid under the maintained minimal-left invariant.
// #
// # Lemma 3: At query time for each right, the trie contains exactly pref[s] for
// # all valid starts s in [left, right].
// # Proof:
// # pref[right] is inserted when right becomes available as a start. Whenever left
// # advances, pref[left] is removed before left increments. Since both right and
// # left move only forward, each prefix is inserted once and removed exactly when
// # its start leaves the valid range.
// #
// # Lemma 4: For any valid start s, the trie query value
// # pref[right + 1] XOR pref[s] equals XOR(nums[s..right]).
// # Proof:
// # This is the standard prefix-XOR identity. Values before s appear twice in the
// # XOR and cancel out.
// #
// # Lemma 5: The binary trie query returns the maximum XOR with the stored prefixes.
// # Proof:
// # XOR value is maximized lexicographically from the highest bit to the lowest.
// # At each bit, choosing the opposite bit of the query number makes the current
// # answer bit 1, which is always better than 0 if such a stored prefix exists.
// # Counts ensure only currently active prefixes are considered.
// #
// # Theorem: The algorithm returns the maximum XOR over all subarrays satisfying
// # max - min <= k.
// # Proof:
// # For each right, Lemma 2 characterizes exactly the valid starts. Lemma 3 says
// # the trie stores exactly their prefix XORs. Lemma 4 converts each candidate
// # start into the corresponding subarray XOR, and Lemma 5 chooses the maximum one.
// # Taking the maximum over all right endpoints considers every valid subarray
// # exactly when its right endpoint is processed.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums), and B = 15 because nums[i] < 2^15.
// #
// # Time:
// #   - Each index enters and leaves each monotonic queue at most once: O(n).
// #   - Each prefix is inserted once and removed at most once from the trie.
// #   - Each trie insert/remove/query costs O(B).
// #   Overall time complexity: O(n * B), which is O(n) here because B = 15.
// #
// # Space:
// #   - The queues store O(n) indices in the worst case.
// #   - The trie stores O(n * B) nodes in the worst case.
// #   - The prefix list stores O(n) values.
// #   Overall space complexity: O(n * B), or O(n) with fixed B.
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [5, 4, 5, 6], k = 2 -> 7
// #      Best subarray is [4, 5, 6].
// #
// # 2. Example 2:
// #      nums = [5, 4, 5, 6], k = 1 -> 6
// #      Single-element [6] is best.
// #
// # 3. k = 0:
// #      Only subarrays whose elements are all equal are valid.
// #
// # 4. Single element:
// #      nums = [x], any k >= 0 -> x.
// #
// # 5. All values within range:
// #      If max(nums) - min(nums) <= k, every subarray is valid, so the problem
// #      becomes normal maximum subarray XOR.
// #
// # 6. Randomized brute force:
// #      For small n, enumerate every subarray, check max-min <= k, and compare
// #      against this solution. This is excellent for catching window/trie deletion
// #      mistakes.
// #
// #
// # Edge cases
// #
// # - nums[i] can be 0; prefix XOR and trie handle zero normally.
// # - Duplicate prefix XORs are allowed. Trie counts preserve multiplicity.
// # - k can be 0; the sliding window still works.
// # - The answer is at least max(nums), because every single-element subarray is
// #   valid.
// #
// #
// # Possible improvements
// #
// # - Since B is only 15, the trie is already tiny. A linear basis does not work
// #   directly here because we need max XOR with one selected prefix from a dynamic
// #   sliding set, not XOR of an arbitrary subset.
// # - A segment tree over time windows would be more complex and unnecessary.
// # - If values had many more bits, this same algorithm would become O(n * B),
// #   where B is the bit width of the maximum prefix XOR.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// from collections import deque
// from typing import List
// 
// 
// class BinaryTrie:
//     MAX_BIT = 14
// 
//     def __init__(self) -> None:
//         self.child = [[-1, -1]]
//         self.count = [0]
// 
//     def insert(self, value: int) -> None:
//         node = 0
//         self.count[node] += 1
//         for bit_index in range(self.MAX_BIT, -1, -1):
//             bit = (value >> bit_index) & 1
//             nxt = self.child[node][bit]
//             if nxt == -1:
//                 nxt = len(self.child)
//                 self.child[node][bit] = nxt
//                 self.child.append([-1, -1])
//                 self.count.append(0)
//             node = nxt
//             self.count[node] += 1
// 
//     def remove(self, value: int) -> None:
//         node = 0
//         self.count[node] -= 1
//         for bit_index in range(self.MAX_BIT, -1, -1):
//             bit = (value >> bit_index) & 1
//             node = self.child[node][bit]
//             self.count[node] -= 1
// 
//     def max_xor(self, value: int) -> int:
//         node = 0
//         best = 0
//         for bit_index in range(self.MAX_BIT, -1, -1):
//             bit = (value >> bit_index) & 1
//             preferred = bit ^ 1
//             preferred_node = self.child[node][preferred]
// 
//             if preferred_node != -1 and self.count[preferred_node] > 0:
//                 best |= 1 << bit_index
//                 node = preferred_node
//             else:
//                 node = self.child[node][bit]
// 
//         return best
// 
// 
// class Solution:
//     def maxXor(self, nums: List[int], k: int) -> int:
//         trie = BinaryTrie()
//         max_q = deque()
//         min_q = deque()
//         prefixes = [0]
// 
//         left = 0
//         current_prefix = 0
//         ans = 0
// 
//         for right, value in enumerate(nums):
//             trie.insert(prefixes[right])
// 
//             while max_q and nums[max_q[-1]] <= value:
//                 max_q.pop()
//             max_q.append(right)
// 
//             while min_q and nums[min_q[-1]] >= value:
//                 min_q.pop()
//             min_q.append(right)
// 
//             while nums[max_q[0]] - nums[min_q[0]] > k:
//                 trie.remove(prefixes[left])
//                 if max_q[0] == left:
//                     max_q.popleft()
//                 if min_q[0] == left:
//                     min_q.popleft()
//                 left += 1
// 
//             current_prefix ^= value
//             ans = max(ans, trie.max_xor(current_prefix))
//             prefixes.append(current_prefix)
// 
//         return ans
// 
// 
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

class BinaryTrie {
    static constexpr int MAX_BIT = 14;
    vector<array<int, 2>> child{{-1, -1}};
    vector<int> count{0};
public:
    void insert(int value) {
        int node = 0;
        ++count[node];
        for (int bit = MAX_BIT; bit >= 0; --bit) {
            int b = (value >> bit) & 1;
            if (child[node][b] == -1) {
                child[node][b] = child.size();
                child.push_back({-1, -1});
                count.push_back(0);
            }
            node = child[node][b];
            ++count[node];
        }
    }
    void remove(int value) {
        int node = 0;
        --count[node];
        for (int bit = MAX_BIT; bit >= 0; --bit) {
            int b = (value >> bit) & 1;
            node = child[node][b];
            --count[node];
        }
    }
    int maxXor(int value) {
        int node = 0, best = 0;
        for (int bit = MAX_BIT; bit >= 0; --bit) {
            int b = (value >> bit) & 1, pref = b ^ 1;
            int pn = child[node][pref];
            if (pn != -1 && count[pn] > 0) {
                best |= 1 << bit;
                node = pn;
            } else {
                node = child[node][b];
            }
        }
        return best;
    }
};

class Solution {
public:
    int maxXor(vector<int>& nums, int k) {
        BinaryTrie trie;
        deque<int> maxQ, minQ;
        vector<int> prefixes{0};
        int left = 0, cur = 0, ans = 0;
        for (int right = 0; right < (int)nums.size(); ++right) {
            int value = nums[right];
            trie.insert(prefixes[right]);
            while (!maxQ.empty() && nums[maxQ.back()] <= value) maxQ.pop_back();
            maxQ.push_back(right);
            while (!minQ.empty() && nums[minQ.back()] >= value) minQ.pop_back();
            minQ.push_back(right);
            while (nums[maxQ.front()] - nums[minQ.front()] > k) {
                trie.remove(prefixes[left]);
                if (maxQ.front() == left) maxQ.pop_front();
                if (minQ.front() == left) minQ.pop_front();
                ++left;
            }
            cur ^= value;
            ans = max(ans, trie.maxXor(cur));
            prefixes.push_back(cur);
        }
        return ans;
    }
};
// @lc code=end
