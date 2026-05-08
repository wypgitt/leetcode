// Translated from 382.linked-list-random-node.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=382 lang=python3
// #
// # [382] Linked List Random Node
// #
// # https://leetcode.com/problems/linked-list-random-node/description/
// #
// # algorithms
// # Medium (64.80%)
// # Likes:    3223
// # Dislikes: 723
// # Total Accepted:    290.2K
// # Total Submissions: 447.8K
// # Testcase Example:  '["Solution","getRandom","getRandom","getRandom","getRandom","getRandom"]\n' +
// # '[[[1,2,3]],[],[],[],[],[]]'
// #
// # Given a singly linked list, return a random node's value from the linked
// # list. Each node must have the same probability of being chosen.
// # 
// # Implement the Solution class:
// # 
// # 
// # Solution(ListNode head) Initializes the object with the head of the
// # singly-linked list head.
// # int getRandom() Chooses a node randomly from the list and returns its value.
// # All the nodes of the list should be equally likely to be chosen.
// # 
// # 
// # 
// # Example 1:
// # 
// # 
// # Input
// # ["Solution", "getRandom", "getRandom", "getRandom", "getRandom", "getRandom"]
// # [[[1, 2, 3]], [], [], [], [], []]
// # Output
// # [null, 1, 3, 2, 2, 3]
// # 
// # Explanation
// # Solution solution = new Solution([1, 2, 3]);
// # solution.getRandom(); // return 1
// # solution.getRandom(); // return 3
// # solution.getRandom(); // return 2
// # solution.getRandom(); // return 2
// # solution.getRandom(); // return 3
// # // getRandom() should return either 1, 2, or 3 randomly. Each element should
// # have equal probability of returning.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # The number of nodes in the linked list will be in the range [1, 10^4].
// # -10^4 <= Node.val <= 10^4
// # At most 10^4 calls will be made to getRandom.
// # 
// # 
// # 
// # Follow up:
// # 
// # 
// # What if the linked list is extremely large and its length is unknown to
// # you?
// # Could you solve this efficiently without using extra space?
// # 
// # 
// #
// 
// # @lc code=start
// import random
// from typing import Optional
// 
// 
// # Definition for singly-linked list.
// # class ListNode:
// #     def __init__(self, val=0, next=None):
// #         self.val = val
// #         self.next = next
// class Solution:
//     """
//     Interview explanation
//     =====================
// 
//     Restate the problem
//     -------------------
//     We are given the head of a singly linked list.  Every time `getRandom()` is
//     called, we must return one node's value, and every node must have exactly the
//     same probability of being chosen.
// 
//     If the list has n nodes, each node should be returned with probability:
// 
//         1 / n
// 
//     Key challenge
//     -------------
//     A linked list does not support O(1) random indexing like an array.  If we do
//     not know the length in advance, we also cannot simply generate a random
//     index from `[0, n - 1]` before walking the list.
// 
//     Two possible approaches
//     -----------------------
//     Approach 1: Preprocess into an array
// 
//         __init__:
//             walk the list and store all values in an array
// 
//         getRandom:
//             return a random array element
// 
//         Time:
//             __init__     O(n)
//             getRandom    O(1)
// 
//         Space:
//             O(n)
// 
//     This is good when memory is acceptable and there are many calls.
// 
//     Approach 2: Reservoir sampling
// 
//         __init__:
//             store only the head pointer
// 
//         getRandom:
//             walk the linked list once and keep one candidate value
// 
//         Time:
//             __init__     O(1)
//             getRandom    O(n)
// 
//         Space:
//             O(1)
// 
//     This directly answers the follow-up: the list can be extremely large, its
//     length can be unknown, and we do not need extra storage.
// 
//     Chosen algorithm: reservoir sampling
//     ------------------------------------
//     Reservoir sampling is designed for choosing a uniformly random item from a
//     stream when:
// 
//     * we do not know the stream length ahead of time
//     * we cannot store all items
//     * each item must have equal probability
// 
//     A linked list can be treated as a stream: node 1, node 2, node 3, ...
// 
//     Algorithm
//     ---------
//     Walk through the list while counting how many nodes have been seen.
// 
//     For the i-th node:
// 
//         choose this node with probability 1 / i
// 
//     If chosen, replace the current answer with this node's value.
// 
//     At the end, return the final candidate.
// 
//     In code, when `nodes_seen == i`, this line makes the replacement decision:
// 
//         if random.randrange(nodes_seen) == 0:
// 
//     `random.randrange(i)` returns one of `0, 1, ..., i - 1` uniformly, so the
//     probability of returning 0 is exactly `1 / i`.
// 
//     Why this is uniform
//     -------------------
//     Consider a specific node at position i in a list of length n.
// 
//     It is selected when we first visit it with probability:
// 
//         1 / i
// 
//     Then it must survive every later replacement decision.
// 
//     At position i + 1, it survives with probability:
// 
//         1 - 1 / (i + 1) = i / (i + 1)
// 
//     At position i + 2, it survives with probability:
// 
//         1 - 1 / (i + 2) = (i + 1) / (i + 2)
// 
//     Continuing through n, the final probability is:
// 
//         (1 / i)
//         * (i / (i + 1))
//         * ((i + 1) / (i + 2))
//         * ...
//         * ((n - 1) / n)
// 
//     Everything cancels:
// 
//         1 / n
// 
//     Therefore every node has exactly the same probability.
// 
//     Data structure choice
//     ---------------------
//     We store only:
// 
//     * `self.head`: the start of the linked list
//     * a few local variables during `getRandom`
// 
//     We intentionally do not use an array because the follow-up asks for an
//     efficient solution without extra space when the list is extremely large or
//     its length is unknown.
// 
//     Correctness proof
//     -----------------
//     Lemma 1: After processing i nodes, each of the first i nodes is the current
//     candidate with probability `1 / i`.
// 
//     Base case:
//     After processing the first node, it is chosen with probability 1, which is
//     `1 / 1`.
// 
//     Inductive step:
//     Assume after processing i - 1 nodes, each previous node is the candidate
//     with probability `1 / (i - 1)`.
// 
//     When processing node i:
// 
//     * node i becomes the candidate with probability `1 / i`
//     * each previous candidate survives with probability `1 - 1 / i`
// 
//     So a previous node remains candidate with probability:
// 
//         (1 / (i - 1)) * (1 - 1 / i)
//       = (1 / (i - 1)) * ((i - 1) / i)
//       = 1 / i
// 
//     Thus after processing i nodes, every one of the first i nodes has
//     probability `1 / i`.
// 
//     Theorem: After processing the whole list of n nodes, `getRandom()` returns
//     each node with probability `1 / n`.
//     This follows directly from Lemma 1 with `i = n`.
// 
//     Complexity analysis
//     -------------------
//     Let n be the number of nodes.
// 
//     Constructor:
// 
//         Time:  O(1)
//         Space: O(1)
// 
//     `getRandom()`:
// 
//         Time:  O(n)
//         Space: O(1)
// 
//     This is the expected tradeoff for reservoir sampling.
// 
//     Edge cases
//     ----------
//     * One node:
//       The first node is selected with probability 1 and returned.
// 
//     * Negative values:
//       Values are returned as-is.  Randomness depends on node position, not value.
// 
//     * Duplicate values:
//       The problem says nodes should be equally likely.  If two nodes have the
//       same value, that value may appear more often because multiple distinct
//       nodes contain it.  That is correct.
// 
//     * Very large list:
//       We do not store all values, so memory stays O(1).
// 
//     Test strategy
//     -------------
//     Random algorithms should not be tested by expecting one fixed random output.
//     Useful tests:
// 
//     * Single-node list always returns that value.
//     * Returned values always belong to the list.
//     * Deterministic monkey-patched random choices can force selection of the
//       first, middle, or last node.
//     * For a statistical smoke test, run many calls with a fixed seed and verify
//       that every value appears at least once.  Do not make strict probability
//       assertions in unit tests because that can be flaky.
// 
//     Possible improvement
//     --------------------
//     If the interviewer prioritizes very fast `getRandom()` calls and allows O(n)
//     memory, preprocessing into an array is better:
// 
//         __init__ O(n), getRandom O(1), space O(n)
// 
//     For the follow-up constraint, reservoir sampling is the stronger answer.
//     """
// 
//     def __init__(self, head: Optional["ListNode"]):
//         self.head = head
// 
//     def getRandom(self) -> int:
//         current = self.head
//         nodes_seen = 0
//         chosen_value = 0
// 
//         while current:
//             nodes_seen += 1
//             if random.randrange(nodes_seen) == 0:
//                 chosen_value = current.val
//             current = current.next
// 
//         return chosen_value
// 
// 
// # Your Solution object will be instantiated and called as such:
// # obj = Solution(head)
// # param_1 = obj.getRandom()
// # @lc code=end
// 
// 
// if __name__ == "__main__":
//     class ListNode:
//         def __init__(self, val=0, next=None):
//             self.val = val
//             self.next = next
// 
//     def build_list(values: list[int]) -> ListNode:
//         dummy = ListNode()
//         tail = dummy
//         for value in values:
//             tail.next = ListNode(value)
//             tail = tail.next
//         return dummy.next
// 
//     def force_random_returns(forced_values: list[int]) -> None:
//         values = forced_values[:]
// 
//         def fake_randrange(stop: int) -> int:
//             value = values.pop(0)
//             assert 0 <= value < stop
//             return value
// 
//         random.randrange = fake_randrange
// 
//     original_randrange = random.randrange
// 
//     single = Solution(build_list([42]))
//     force_random_returns([0])
//     assert single.getRandom() == 42
// 
//     head = build_list([10, 20, 30])
// 
//     force_random_returns([0, 1, 1])
//     assert Solution(head).getRandom() == 10
// 
//     force_random_returns([0, 0, 1])
//     assert Solution(head).getRandom() == 20
// 
//     force_random_returns([0, 1, 0])
//     assert Solution(head).getRandom() == 30
// 
//     random.randrange = original_randrange
//     random.seed(0)
// 
//     solution = Solution(head)
//     results = [solution.getRandom() for _ in range(200)]
//     assert set(results) == {10, 20, 30}

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
    ListNode* head;
    mt19937 rng{random_device{}()};

public:
    Solution(ListNode* head) : head(head) {}

    int getRandom() {
        ListNode* cur = head;
        int seen = 0, chosen = 0;
        while (cur) {
            ++seen;
            uniform_int_distribution<int> dist(0, seen - 1);
            if (dist(rng) == 0) chosen = cur->val;
            cur = cur->next;
        }
        return chosen;
    }
};
