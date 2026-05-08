// Translated from 481.magical-string.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=481 lang=python3
// #
// # [481] Magical String
// #
// # https://leetcode.com/problems/magical-string/description/
// #
// # algorithms
// # Medium (55.11%)
// # Likes:    383
// # Dislikes: 1425
// # Total Accepted:    56.6K
// # Total Submissions: 102.7K
// # Testcase Example:  '6'
// #
// # A magical string s consists of only '1' and '2' and obeys the following
// # rule:
// # 
// # 
// # Concatenating the sequence of lengths of its consecutive groups of identical
// # characters '1' and '2' generates the string s itself.
// # 
// # 
// # The first few elements of s is s = "1221121221221121122……". If we group the
// # consecutive 1's and 2's in s, it will be "1 22 11 2 1 22 1 22 11 2 11 22
// # ......" and counting the occurrences of 1's or 2's in each group yields the
// # sequence "1 2 2 1 1 2 1 2 2 1 2 2 ......".
// # 
// # You can see that concatenating the occurrence sequence gives us s itself.
// # 
// # Given an integer n, return the number of 1's in the first n number in the
// # magical string s.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: n = 6
// # Output: 3
// # Explanation: The first 6 elements of magical string s is "122112" and it
// # contains three 1's, so return 3.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: n = 1
// # Output: 1
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n <= 10^5
// # 
// # 
// #
// 
// # @lc code=start
// class Solution:
//     def magicalString(self, n: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         The magical string is made only of `1` and `2`:
// 
//             1221121221221121122...
// 
//         If we group consecutive equal characters:
// 
//             1 | 22 | 11 | 2 | 1 | 22 | 1 | 22 | ...
// 
//         and write down the group lengths:
// 
//             1, 2, 2, 1, 1, 2, 1, 2, ...
// 
//         we get the magical string itself.
// 
//         Given `n`, return how many `1`s appear in the first `n` characters of
//         this infinite magical string.
// 
//         Key observation
//         ---------------
//         The string tells us how to generate itself.
// 
//         Each number in the magical string is either:
// 
//             1 -> the next group has length 1
//             2 -> the next group has length 2
// 
//         The group values alternate between `1` and `2`:
// 
//             group value 1, then 2, then 1, then 2, ...
// 
//         Starting prefix:
// 
//             s = [1, 2, 2]
// 
//         This already represents:
// 
//             first group: one `1`
//             second group: two `2`s
// 
//         The next unread group length is at index 2, whose value is `2`, meaning:
// 
//             append two copies of the next group value, which is `1`
// 
//         giving:
// 
//             [1, 2, 2, 1, 1]
// 
//         Then the next unread group length is at index 3, whose value is `1`,
//         meaning append one copy of the next group value, which is `2`.
// 
//         Data structure choice
//         ---------------------
//         We use a list of integers to store the generated prefix.
// 
//         Why:
// 
//         * we need random access to `s[read]`, the next group length
//         * appending to a Python list is O(1) amortized
//         * values are only `1` and `2`, so memory is small for n <= 100000
// 
//         Variables
//         ---------
//         * `magical`
//           The generated prefix of the magical string.
// 
//         * `read`
//           Index of the next value in `magical` that tells us the length of the
//           next group to append.
// 
//         * `next_value`
//           The value of the next group to append, either 1 or 2.
// 
//         * `ones`
//           Count of `1`s among the first `n` generated characters.
// 
//         Algorithm
//         ---------
//         1. Handle small `n`:
// 
//                n = 1 -> first character is 1
//                n = 2 or 3 -> prefix is 122, which has one 1
// 
//         2. Start:
// 
//                magical = [1, 2, 2]
//                read = 2
//                next_value = 1
//                ones = 1
// 
//         3. While `len(magical) < n`:
//               - `repeat = magical[read]`
//               - append `next_value` exactly `repeat` times
//               - if an appended value is `1` and it lies inside the first `n`
//                 positions, increment `ones`
//               - flip `next_value` between 1 and 2
//               - move `read` forward
// 
//         4. Return `ones`.
// 
//         Why count during generation?
//         ----------------------------
//         We could generate the prefix and then call `magical[:n].count(1)`.
//         Counting while appending avoids a second pass and is just as clear.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: At every iteration, `magical[read]` is the correct length of
//         the next group to append.
//         The magical string's defining property says the sequence of group
//         lengths equals the string itself.  Since `magical` stores the generated
//         prefix of that string, reading the next unused value from `magical` gives
//         the next group length.
// 
//         Lemma 2: `next_value` is the correct value for the next group.
//         Groups in the magical string alternate between runs of `1` and runs of
//         `2`.  The initial prefix `[1, 2, 2]` has already generated the first two
//         groups: `1` and `22`.  Therefore the next group value is `1`.  After
//         every appended group, the algorithm flips `next_value`, preserving the
//         alternation.
// 
//         Lemma 3: After each iteration, `magical` is a valid prefix of the
//         magical string.
//         By Lemma 1, the algorithm uses the correct next group length.  By
//         Lemma 2, it uses the correct next group value.  Appending that group
//         therefore extends the prefix exactly as the magical string definition
//         requires.
// 
//         Lemma 4: `ones` equals the number of `1`s among the first `n` generated
//         positions.
//         It starts as 1 for the initial prefix `[1, 2, 2]`, which is correct for
//         the first three positions.  During generation, the algorithm increments
//         `ones` exactly when it appends a `1` whose index is still less than `n`.
//         It never counts positions beyond `n`.
// 
//         Theorem: The algorithm returns the number of `1`s in the first `n`
//         characters of the magical string.
//         By Lemma 3, the algorithm generates the magical string prefix correctly
//         until it has at least `n` characters.  By Lemma 4, `ones` is exactly the
//         count of `1`s in the first `n` positions of that prefix.  Therefore the
//         returned value is correct.
// 
//         Complexity analysis
//         -------------------
//         We append characters until the generated prefix has length at least `n`.
//         Each append is O(1) amortized.
// 
//         Total time:  O(n)
//         Total space: O(n)
// 
//         Edge cases
//         ----------
//         * n = 1:
//           The answer is 1.
// 
//         * n = 2 or n = 3:
//           The prefix is `122`, so the answer is 1.
// 
//         * The last appended group may pass length n:
//           We still append it, but we only increment the count if the appended
//           position is inside the first n characters.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               n = 6 -> 3
//               n = 1 -> 1
// 
//         * Small prefixes:
//               n = 2 -> 1
//               n = 3 -> 1
//               n = 4 -> 2
//               n = 5 -> 3
// 
//         * Larger values:
//           Compare against a simple reference generator or known accepted
//           solutions.
// 
//         Possible improvement?
//         ---------------------
//         O(n) time is optimal because the answer depends on the first `n`
//         generated characters.  Space can be reduced slightly with a queue-like
//         structure, but we still need access to future group lengths, and the
//         O(n) list is simple and well within the constraints.
//         """
// 
//         if n <= 3:
//             return 1
// 
//         magical = [1, 2, 2]
//         read = 2
//         next_value = 1
//         ones = 1
// 
//         while len(magical) < n:
//             repeat = magical[read]
// 
//             for _ in range(repeat):
//                 magical.append(next_value)
//                 if next_value == 1 and len(magical) <= n:
//                     ones += 1
// 
//             next_value = 3 - next_value
//             read += 1
// 
//         return ones
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
    int magicalString(int n) {
        if (n <= 3) return 1;
        vector<int> magical{1, 2, 2};
        int read = 2, nextValue = 1, ones = 1;
        while ((int)magical.size() < n) {
            int repeat = magical[read++];
            while (repeat--) {
                magical.push_back(nextValue);
                if (nextValue == 1 && (int)magical.size() <= n) ++ones;
            }
            nextValue = 3 - nextValue;
        }
        return ones;
    }
};
