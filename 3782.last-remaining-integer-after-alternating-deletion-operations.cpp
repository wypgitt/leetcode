// Translated from 3782.last-remaining-integer-after-alternating-deletion-operations.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3782 lang=python3
// #
// # [3782] Last Remaining Integer After Alternating Deletion Operations
// #
// # https://leetcode.com/problems/last-remaining-integer-after-alternating-deletion-operations/description/
// #
// # algorithms
// # Hard (48.60%)
// # Likes:    39
// # Dislikes: 4
// # Total Accepted:    7.8K
// # Total Submissions: 16.1K
// # Testcase Example:  '8'
// #
// # You are given an integer n.
// # 
// # We write the integers from 1 to n in a sequence from left to right. Then,
// # alternately apply the following two operations until only one integer
// # remains, starting with operation 1:
// # 
// # 
// # Operation 1: Starting from the left, delete every second number.
// # Operation 2: Starting from the right, delete every second number.
// # 
// # 
// # Return the last remaining integer.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: n = 8
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # 
// # Write [1, 2, 3, 4, 5, 6, 7, 8] in a sequence.
// # Starting from the left, we delete every second number: [1, 2, 3, 4, 5, 6, 7,
// # 8]. The remaining integers are [1, 3, 5, 7].
// # Starting from the right, we delete every second number: [1, 3, 5, 7]. The
// # remaining integers are [3, 7].
// # Starting from the left, we delete every second number: [3, 7]. The remaining
// # integer is [3].
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: n = 5
// # 
// # Output: 1
// # 
// # Explanation:
// # 
// # 
// # Write [1, 2, 3, 4, 5] in a sequence.
// # Starting from the left, we delete every second number: [1, 2, 3, 4, 5]. The
// # remaining integers are [1, 3, 5].
// # Starting from the right, we delete every second number: [1, 3, 5]. The
// # remaining integers are [1, 5].
// # Starting from the left, we delete every second number: [1, 5]. The remaining
// # integer is [1].
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: n = 1
// # 
// # Output: 1
// # 
// # Explanation:
// # 
// # 
// # Write [1] in a sequence.
// # The last remaining integer is 1.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n <= 10^15
// # 
// # 
// #
// 
// # @lc code=start
// class Solution:
//     def lastInteger(self, n: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         Start with:
// 
//             [1, 2, 3, ..., n]
// 
//         Then repeatedly alternate two operations:
// 
//         * Operation 1, from the left:
//           delete every second number.
// 
//         * Operation 2, from the right:
//           delete every second number.
// 
//         The examples show that "delete every second number" means the first
//         number encountered is kept, the second is deleted, the third is kept,
//         and so on.
// 
//         For example:
// 
//             [1, 2, 3, 4, 5, 6, 7, 8]
// 
//         After a left pass:
// 
//             [1, 3, 5, 7]
// 
//         We need the last remaining integer for `n` up to `10^15`.
// 
//         Why not simulate the list?
//         --------------------------
//         A direct list simulation would store up to `10^15` numbers, which is
//         impossible.
// 
//         The key is that after every deletion round, the remaining numbers still
//         form an arithmetic progression.
// 
//         Arithmetic progression state
//         ----------------------------
//         Instead of storing the whole list, store:
// 
//             first = first remaining value
//             step  = difference between consecutive remaining values
//             count = number of remaining values
// 
//         The current sequence is:
// 
//             first,
//             first + step,
//             first + 2 * step,
//             ...
//             first + (count - 1) * step
// 
//         Initially:
// 
//             first = 1
//             step = 1
//             count = n
// 
//         What one deletion round does
//         ----------------------------
//         Each round keeps about half the numbers:
// 
//             new_count = ceil(count / 2)
//                       = (count + 1) // 2
// 
//         Since we keep every other element, the gap doubles:
// 
//             new_step = step * 2
// 
//         The only subtle part is whether the first remaining value changes.
// 
//         Left-to-right pass
//         ------------------
//         Starting from the left, keep the 1st, delete the 2nd, keep the 3rd, ...
// 
//         In 0-based indices, we keep:
// 
//             0, 2, 4, ...
// 
//         So the first element stays the same:
// 
//             first does not change
// 
//         Right-to-left pass
//         ------------------
//         Starting from the right, keep the rightmost element, delete the next,
//         keep the next, and so on.
// 
//         In 0-based indices from the left, an index `i` is kept when:
// 
//             (count - 1 - i) is even
// 
//         This means:
// 
//         * if `count` is odd, kept indices are:
// 
//               0, 2, 4, ...
// 
//           so the first element stays.
// 
//         * if `count` is even, kept indices are:
// 
//               1, 3, 5, ...
// 
//           so the first element moves forward by one old `step`.
// 
//         Therefore, on a right-to-left pass:
// 
//             if count is even:
//                 first += step
// 
//         Data structure choice
//         ---------------------
//         No list, queue, or tree is needed.  The sequence remains an arithmetic
//         progression, so three integers are enough:
// 
//         * `first`
//         * `step`
//         * `count`
// 
//         Plus one boolean to track direction.
// 
//         Algorithm
//         ---------
//         1. Initialize:
// 
//                first = 1
//                step = 1
//                count = n
//                delete_from_left = True
// 
//         2. While `count > 1`:
//               * if this is a right-to-left pass and `count` is even, advance
//                 `first` by `step`
//               * set `count = (count + 1) // 2`
//               * set `step *= 2`
//               * flip the direction
// 
//         3. Return `first`.
// 
//         Walkthrough
//         -----------
//         For `n = 8`:
// 
//             first = 1, step = 1, count = 8
// 
//         Left pass:
// 
//             keep [1, 3, 5, 7]
//             first = 1, step = 2, count = 4
// 
//         Right pass:
// 
//             count is even, so first += step -> 3
//             keep [3, 7]
//             first = 3, step = 4, count = 2
// 
//         Left pass:
// 
//             keep [3]
//             first = 3, step = 8, count = 1
// 
//         Answer:
// 
//             3
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Before every round, the remaining sequence is represented
//         exactly by `(first, step, count)`.
//         Initially this is true for `[1, 2, ..., n]`.  A round keeps every other
//         element of an arithmetic progression, which is still an arithmetic
//         progression with doubled step and about half as many elements.
// 
//         Lemma 2: A left-to-right round never changes `first`.
//         The first encountered element is kept, so index 0 of the current
//         sequence remains.
// 
//         Lemma 3: A right-to-left round changes `first` exactly when `count` is
//         even.
//         A right-to-left round keeps indices `i` satisfying
//         `(count - 1 - i) % 2 == 0`.  If `count` is odd, index 0 is kept.  If
//         `count` is even, index 0 is deleted and index 1 becomes first, which is
//         `first + step`.
// 
//         Theorem: The algorithm returns the last remaining integer.
//         By Lemma 1, the state always represents the exact remaining sequence.
//         By Lemma 2 and Lemma 3, each round updates the first element correctly.
//         The count and step updates are exactly the result of keeping every other
//         element.  When `count == 1`, the represented sequence has only one
//         value, namely `first`, so returning `first` is correct.
// 
//         Complexity analysis
//         -------------------
//         Each round reduces `count` to `ceil(count / 2)`, so the number of rounds
//         is O(log n).
// 
//         Time:
// 
//             O(log n)
// 
//         Space:
// 
//             O(1)
// 
//         Edge cases
//         ----------
//         * n = 1:
//           The loop never runs and the answer is 1.
// 
//         * n = 2:
//           Left pass keeps the first number, so answer is 1.
// 
//         * Odd count on a right pass:
//           The leftmost element survives, so `first` does not move.
// 
//         * Very large n:
//           We store only a few integers, so `10^15` is easy.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               n = 8 -> 3
//               n = 5 -> 1
//               n = 1 -> 1
// 
//         * Small values compared with direct simulation.
//         * Powers of two.
//         * Large value such as `10^15` to confirm performance.
// 
//         Possible improvement
//         --------------------
//         This O(log n), O(1)-space simulation of the arithmetic progression is
//         already optimal for an interview.  A closed-form recurrence may exist,
//         but it is harder to explain and less robust than the state update.
//         """
// 
//         first = 1
//         step = 1
//         count = n
//         delete_from_left = True
// 
//         while count > 1:
//             if not delete_from_left and count % 2 == 0:
//                 first += step
// 
//             count = (count + 1) // 2
//             step *= 2
//             delete_from_left = not delete_from_left
// 
//         return first
// # @lc code=end
// 
// 
// if __name__ == "__main__":
//     def brute_force_last_integer(value: int) -> int:
//         numbers = list(range(1, value + 1))
//         delete_from_left = True
// 
//         while len(numbers) > 1:
//             if delete_from_left:
//                 numbers = numbers[::2]
//             else:
//                 keep = [False] * len(numbers)
//                 keep_from_right = True
// 
//                 for index in range(len(numbers) - 1, -1, -1):
//                     if keep_from_right:
//                         keep[index] = True
//                     keep_from_right = not keep_from_right
// 
//                 numbers = [
//                     number
//                     for index, number in enumerate(numbers)
//                     if keep[index]
//                 ]
// 
//             delete_from_left = not delete_from_left
// 
//         return numbers[0]
// 
//     solution = Solution()
// 
//     fixed_tests = {
//         1: 1,
//         2: 1,
//         3: 3,
//         4: 3,
//         5: 1,
//         8: 3,
//         16: 11,
//     }
// 
//     for test_n, expected in fixed_tests.items():
//         assert solution.lastInteger(test_n) == expected
// 
//     for test_n in range(1, 200):
//         expected = brute_force_last_integer(test_n)
//         assert solution.lastInteger(test_n) == expected, test_n
// 
//     assert solution.lastInteger(10**15) > 0

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
    long long lastInteger(long long n) {
        long long first = 1, step = 1, count = n;
        bool deleteFromLeft = true;
        while (count > 1) {
            if (!deleteFromLeft && count % 2 == 0) first += step;
            count = (count + 1) / 2;
            step *= 2;
            deleteFromLeft = !deleteFromLeft;
        }
        return first;
    }
};
