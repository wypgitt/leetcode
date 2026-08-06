/*
 * @lc app=leetcode id=3889 lang=cpp
 *
 * [3889] Mirror Frequency Distance
 */
// Translated from 3889.mirror-frequency-distance.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3889 lang=python3
// #
// # [3889] Mirror Frequency Distance
// #
// # https://leetcode.com/problems/mirror-frequency-distance/description/
// #
// # algorithms
// # Medium (60.84%)
// # Likes:    46
// # Dislikes: 8
// # Total Accepted:    41.7K
// # Total Submissions: 68.6K
// # Testcase Example:  '"ab1z9"'
// #
// # You are given a string s consisting of lowercase English letters and digits.
// # 
// # For each character, its mirror character is defined by reversing the order of
// # its character set:
// # 
// # 
// # For letters, the mirror of a character is the letter at the same position
// # from the end of the alphabet.
// # 
// # For example, the mirror of 'a' is 'z', and the mirror of 'b' is 'y', and so
// # on.
// # 
// # 
// # For digits, the mirror of a character is the digit at the same position from
// # the end of the range '0' to '9'.
// # 
// # For example, the mirror of '0' is '9', and the mirror of '1' is '8', and so
// # on.
// # 
// # 
// # 
// # 
// # For each unique character c in the string:
// # 
// # 
// # Let m be its mirror character.
// # Let freq(x) denote the number of times character x appears in the string.
// # Compute the absolute difference between their frequencies, defined as:
// # |freq(c) - freq(m)|
// # 
// # 
// # The mirror pairs (c, m) and (m, c) are the same and must be counted only
// # once.
// # 
// # Return an integer denoting the total sum of these values over all such
// # distinct mirror pairs.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: s = "ab1z9"
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # For every mirror pair:
// # 
// # 
// # 
// # 
// # c
// # m
// # freq(c)
// # freq(m)
// # |freq(c) - freq(m)|
// # 
// # 
// # 
// # 
// # a
// # z
// # 1
// # 1
// # 0
// # 
// # 
// # b
// # y
// # 1
// # 0
// # 1
// # 
// # 
// # 1
// # 8
// # 1
// # 0
// # 1
// # 
// # 
// # 9
// # 0
// # 1
// # 0
// # 1
// # 
// # 
// # 
// # 
// # Thus, the answer is 0 + 1 + 1 + 1 = 3.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: s = "4m7n"
// # 
// # Output: 2
// # 
// # Explanation:
// # 
// # 
// # 
// # 
// # c
// # m
// # freq(c)
// # freq(m)
// # |freq(c) - freq(m)|
// # 
// # 
// # 
// # 
// # 4
// # 5
// # 1
// # 0
// # 1
// # 
// # 
// # m
// # n
// # 1
// # 1
// # 0
// # 
// # 
// # 7
// # 2
// # 1
// # 0
// # 1
// # 
// # 
// # 
// # 
// # Thus, the answer is 1 + 0 + 1 = 2.​​​​​​​
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: s = "byby"
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # 
// # 
// # 
// # c
// # m
// # freq(c)
// # freq(m)
// # |freq(c) - freq(m)|
// # 
// # 
// # 
// # 
// # b
// # y
// # 2
// # 2
// # 0
// # 
// # 
// # 
// # 
// # Thus, the answer is 0.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= s.length <= 5 * 10^5
// # s consists only of lowercase English letters and digits.
// # 
// # 
// #
// 
// # lc-original code=start
// from collections import Counter
// 
// 
// class Solution:
//     def mirrorFrequency(self, s: str) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given a string containing lowercase English letters and digits.
// 
//         Every character has a mirror:
// 
//         * letters mirror across the alphabet:
//               a <-> z
//               b <-> y
//               c <-> x
//               ...
//               m <-> n
// 
//         * digits mirror across 0..9:
//               0 <-> 9
//               1 <-> 8
//               2 <-> 7
//               3 <-> 6
//               4 <-> 5
// 
//         For each distinct mirror pair, we compute:
// 
//             abs(freq(left) - freq(right))
// 
//         and return the total.
// 
//         Mirror pairs must be counted once
//         ---------------------------------
//         The pair `(a, z)` is the same as `(z, a)`.  We must not add the
//         difference twice.
// 
//         The easiest way to guarantee this is to explicitly iterate only over one
//         side of every pair:
// 
//             letters: a through m
//             digits:  0 through 4
// 
//         These cover all mirror pairs exactly once.
// 
//         Key observation: the alphabet is constant-size
//         ----------------------------------------------
//         Although `s.length` can be as large as 500,000, the set of possible
//         characters is tiny:
// 
//             26 lowercase letters + 10 digits = 36 characters
// 
//         Therefore:
// 
//         1. Count all character frequencies in one pass.
//         2. Check the 13 letter mirror pairs and 5 digit mirror pairs.
// 
//         Data structure choice
//         ---------------------
//         We use `Counter`, a hash map from character to frequency.
// 
//         Why it fits:
// 
//         * counting the string is O(n)
//         * missing characters naturally have count 0
//         * the code directly matches the problem statement: `freq(c)`
// 
//         A fixed-size array of length 36 would also work, but it would require
//         manual character-to-index mapping.  Since the alphabet is tiny and Python
//         dictionaries are efficient, `Counter` keeps the solution clear.
// 
//         Algorithm
//         ---------
//         1. Build `frequency = Counter(s)`.
//         2. Initialize `answer = 0`.
//         3. For each letter pair:
// 
//                left = chr(ord('a') + i)
//                right = chr(ord('z') - i)
//                answer += abs(frequency[left] - frequency[right])
// 
//            for i = 0..12.
// 
//         4. For each digit pair:
// 
//                left = chr(ord('0') + i)
//                right = chr(ord('9') - i)
//                answer += abs(frequency[left] - frequency[right])
// 
//            for i = 0..4.
// 
//         5. Return `answer`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: The algorithm considers every letter mirror pair exactly once.
//         There are 26 letters, forming 13 mirror pairs.  Iterating `i = 0..12`
//         creates pairs:
// 
//             ('a', 'z'), ('b', 'y'), ..., ('m', 'n')
// 
//         This includes every letter exactly once and therefore every letter mirror
//         pair exactly once.
// 
//         Lemma 2: The algorithm considers every digit mirror pair exactly once.
//         There are 10 digits, forming 5 mirror pairs.  Iterating `i = 0..4`
//         creates pairs:
// 
//             ('0', '9'), ('1', '8'), ..., ('4', '5')
// 
//         This includes every digit exactly once and therefore every digit mirror
//         pair exactly once.
// 
//         Lemma 3: For each considered pair `(c, m)`, the algorithm adds the
//         correct contribution.
//         `Counter(s)[c]` is exactly `freq(c)`, and `Counter(s)[m]` is exactly
//         `freq(m)`.  The algorithm adds `abs(freq(c) - freq(m))`, which is the
//         value required by the problem.
// 
//         Theorem: The algorithm returns the required total mirror frequency
//         distance.
//         By Lemma 1 and Lemma 2, every distinct mirror pair is considered exactly
//         once.  By Lemma 3, each pair contributes exactly the required value.
//         Therefore the sum returned by the algorithm is exactly the desired
//         answer.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(s).
// 
//         Building the frequency table costs O(n).  Then we inspect exactly
//         18 mirror pairs: 13 letter pairs and 5 digit pairs, which is O(1).
// 
//         Total time:  O(n)
//         Total space: O(1)
// 
//         The space is O(1) because the Counter can contain at most 36 keys, no
//         matter how long the input string is.
// 
//         Edge cases
//         ----------
//         * A character appears but its mirror does not:
//               "b" contributes abs(1 - 0) = 1 for pair (b, y).
// 
//         * Both sides appear equally often:
//               "byby" contributes abs(2 - 2) = 0.
// 
//         * Digits and letters are independent:
//               'a' only mirrors with 'z'; it never interacts with digits.
// 
//         * Single-character string:
//               the answer is 1, because that character's mirror has frequency 0.
// 
//         * Large input:
//               counting remains linear and memory stays constant.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               "ab1z9" -> 3
//               "4m7n"  -> 2
//               "byby"  -> 0
// 
//         * Single characters:
//               "a" -> 1
//               "0" -> 1
// 
//         * Balanced all pairs:
//               "azby09" -> 0
// 
//         * Unbalanced repeated characters:
//               "aaaaaz" -> 4
// 
//         Possible improvement?
//         ---------------------
//         This is already asymptotically optimal because every character may
//         affect the answer, so we must read the whole string.  A fixed-size array
//         could reduce a small constant factor, but `Counter` is clearer and easily
//         fast enough for 500,000 characters.
//         """
// 
//         frequency = Counter(s)
//         answer = 0
// 
//         for offset in range(13):
//             left = chr(ord("a") + offset)
//             right = chr(ord("z") - offset)
//             answer += abs(frequency[left] - frequency[right])
// 
//         for offset in range(5):
//             left = chr(ord("0") + offset)
//             right = chr(ord("9") - offset)
//             answer += abs(frequency[left] - frequency[right])
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
    int mirrorFrequency(string s) {
        unordered_map<char, int> freq;
        for (char c : s) ++freq[c];
        int ans = 0;
        for (int off = 0; off < 13; ++off) ans += abs(freq[char('a' + off)] - freq[char('z' - off)]);
        for (int off = 0; off < 5; ++off) ans += abs(freq[char('0' + off)] - freq[char('9' - off)]);
        return ans;
    }
};
// @lc code=end
