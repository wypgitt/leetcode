// Translated from 3907.count-smaller-elements-with-opposite-parity.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3907 lang=python3
// #
// # [3907] Count Smaller Elements With Opposite Parity
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # For each index i, count indices j such that:
// #   i < j
// #   nums[j] < nums[i]
// #   nums[j] has opposite parity from nums[i]
// #
// # Return the score for every index.
// #
// # Example:
// #   nums = [5, 2, 4, 1, 3]
// #
// # For i = 0, nums[i] = 5 is odd.
// # Smaller values to the right with opposite parity are 2 and 4.
// # answer[0] = 2.
// #
// #
// # Key observation
// # For each i, we only care about elements to the right of i.
// #
// # If we scan from right to left, the elements already processed are exactly the
// # elements to the right.
// #
// # For current value x:
// #   if x is odd, query how many even processed values are < x
// #   if x is even, query how many odd processed values are < x
// #
// # Then insert x into the data structure for its own parity.
// #
// #
// # Need order statistics
// # Values can be as large as 1e9, so we cannot use a direct frequency array.
// #
// # We need:
// #   - insert a value
// #   - count how many inserted values are strictly smaller than x
// #
// # This is a classic Fenwick tree / Binary Indexed Tree use case after coordinate
// # compression.
// #
// #
// # Coordinate compression
// # Sort the distinct values in nums.
// #
// # Map each value to a rank:
// #   smallest value -> 1
// #   next value     -> 2
// #   ...
// #
// # Fenwick trees operate over these ranks.
// #
// # To count values strictly smaller than x, query rank(x) - 1.
// #
// #
// # Why two Fenwick trees?
// # The parity condition asks for opposite parity only.
// #
// # Maintain:
// #   bit_even: counts of processed even values by rank
// #   bit_odd:  counts of processed odd values by rank
// #
// # For x:
// #   opposite_tree = bit_odd if x is even else bit_even
// #   answer[i] = opposite_tree.query(rank(x) - 1)
// #
// # Then insert x into its own parity tree.
// #
// #
// # Data structure choice: Fenwick tree
// # Fenwick tree supports:
// #   update(rank, +1)      in O(log n)
// #   prefix_sum(rank)      in O(log n)
// #
// # It is simpler and lighter than a segment tree for prefix counts.
// #
// #
// # Walkthrough of the code
// # 1. Compress nums values to ranks.
// # 2. Create two Fenwick trees: one for even values, one for odd values.
// # 3. Scan i from n-1 down to 0:
// #      rank = compressed rank of nums[i]
// #      if nums[i] is even:
// #          answer[i] = odd_tree.query(rank - 1)
// #          even_tree.add(rank, 1)
// #      else:
// #          answer[i] = even_tree.query(rank - 1)
// #          odd_tree.add(rank, 1)
// # 4. Return answer.
// #
// #
// # Correctness proof
// #
// # Lemma 1: When processing index i from right to left, the Fenwick trees contain
// # exactly values nums[j] for j > i, separated by parity.
// # Proof:
// # Initially no elements are processed, matching the empty suffix after the last
// # index. After answering index i, the algorithm inserts nums[i]. Therefore before
// # processing the next index to the left, the trees contain exactly the elements
// # to its right. Induction proves the claim.
// #
// # Lemma 2: For current nums[i] = x, querying the opposite-parity tree at
// # rank(x)-1 returns exactly the number of valid j.
// # Proof:
// # By Lemma 1, the opposite-parity tree contains exactly elements to the right
// # whose parity differs from x. Coordinate compression preserves ordering, so
// # ranks less than rank(x) are exactly values strictly smaller than x. The Fenwick
// # prefix query counts exactly those elements.
// #
// # Theorem: The algorithm returns the correct score for every index.
// # Proof:
// # For every i, Lemma 2 shows the computed answer[i] equals the number of indices
// # j to the right with smaller value and opposite parity. This is exactly the
// # required score.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums).
// #
// # Time:
// #   - Sorting distinct values for compression: O(n log n)
// #   - Each index does one query and one update: O(log n)
// #   Overall time complexity: O(n log n).
// #
// # Space:
// #   - compressed mapping: O(n)
// #   - two Fenwick trees: O(n)
// #   - answer array: O(n)
// #   Overall space complexity: O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [5,2,4,1,3] -> [2,1,2,0,0]
// #
// # 2. Example 2:
// #      nums = [4,4,1] -> [1,1,0]
// #      Duplicates equal to current are not counted because condition is strict.
// #
// # 3. Single element:
// #      nums = [7] -> [0]
// #
// # 4. All same parity:
// #      nums = [2,4,6] -> [0,0,0]
// #
// # 5. Strictly decreasing alternating parity:
// #      Many counts become nonzero.
// #
// # 6. Random brute force:
// #      For small arrays, compare against the O(n^2) definition.
// #
// #
// # Edge cases
// #
// # - Duplicates: strict smaller means query rank - 1, not rank.
// # - Large values: coordinate compression handles up to 1e9.
// # - All odds or all evens: one Fenwick tree remains unused for queries.
// #
// #
// # Possible improvements
// #
// # - If nums[i] had a small bounded value range, direct frequency prefix arrays
// #   could replace Fenwick trees.
// # - A merge-sort counting approach is possible but more complex with parity.
// # - Fenwick tree is the most direct online suffix-count solution.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class Fenwick:
//     def __init__(self, size: int) -> None:
//         self.tree = [0] * (size + 1)
// 
//     def add(self, index: int, delta: int) -> None:
//         while index < len(self.tree):
//             self.tree[index] += delta
//             index += index & -index
// 
//     def query(self, index: int) -> int:
//         total = 0
//         while index > 0:
//             total += self.tree[index]
//             index -= index & -index
//         return total
// 
// 
// class Solution:
//     def countSmallerOppositeParity(self, nums: List[int]) -> List[int]:
//         values = sorted(set(nums))
//         rank = {value: index + 1 for index, value in enumerate(values)}
// 
//         even_tree = Fenwick(len(values))
//         odd_tree = Fenwick(len(values))
//         answer = [0] * len(nums)
// 
//         for i in range(len(nums) - 1, -1, -1):
//             value = nums[i]
//             pos = rank[value]
// 
//             if value % 2 == 0:
//                 answer[i] = odd_tree.query(pos - 1)
//                 even_tree.add(pos, 1)
//             else:
//                 answer[i] = even_tree.query(pos - 1)
//                 odd_tree.add(pos, 1)
// 
//         return answer
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

class Fenwick {
    vector<int> tree;
public:
    Fenwick(int n) : tree(n + 1) {}
    void add(int i, int delta) { while (i < (int)tree.size()) { tree[i] += delta; i += i & -i; } }
    int query(int i) { int total = 0; while (i > 0) { total += tree[i]; i -= i & -i; } return total; }
};

class Solution {
public:
    vector<int> countSmallerOppositeParity(vector<int>& nums) {
        vector<int> values = nums;
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        Fenwick even(values.size()), odd(values.size());
        vector<int> ans(nums.size());
        for (int i = (int)nums.size() - 1; i >= 0; --i) {
            int pos = lower_bound(values.begin(), values.end(), nums[i]) - values.begin() + 1;
            if (nums[i] % 2 == 0) {
                ans[i] = odd.query(pos - 1);
                even.add(pos, 1);
            } else {
                ans[i] = even.query(pos - 1);
                odd.add(pos, 1);
            }
        }
        return ans;
    }
};
