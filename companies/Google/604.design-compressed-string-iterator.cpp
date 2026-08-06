/*
 * @lc app=leetcode id=604 lang=cpp
 *
 * [604] Design Compressed String Iterator
 */
// Translated from 604.design-compressed-string-iterator.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=604 lang=python3
// #
// # [604] Design Compressed String Iterator
// #
// # https://leetcode.com/problems/design-compressed-string-iterator/description/
// #
// # algorithms
// # Easy (40.39%)
// # Likes:    460
// # Dislikes: 167
// # Total Accepted:    39.8K
// # Total Submissions: 98.4K
// # Testcase Example:  '["StringIterator","next","next","next","next","next","next","hasNext","next","hasNext"]\n' +
// # '[["L1e2t1C1o1d1e1"],[],[],[],[],[],[],[],[],[]]'
// #
// # Design and implement a data structure for a compressed string iterator. The
// # given compressed string will be in the form of each letter followed by a
// # positive integer representing the number of this letter existing in the
// # original uncompressed string.
// # 
// # Implement the StringIterator class:
// # 
// # 
// # next() Returns the next character if the original string still has
// # uncompressed characters, otherwise returns a white space.
// # hasNext() Returns true if there is any letter needs to be uncompressed in the
// # original string, otherwise returns false.
// # 
// # 
// # 
// # Example 1:
// # 
// # 
// # Input
// # ["StringIterator", "next", "next", "next", "next", "next", "next", "hasNext",
// # "next", "hasNext"]
// # [["L1e2t1C1o1d1e1"], [], [], [], [], [], [], [], [], []]
// # Output
// # [null, "L", "e", "e", "t", "C", "o", true, "d", true]
// # 
// # Explanation
// # StringIterator stringIterator = new StringIterator("L1e2t1C1o1d1e1");
// # stringIterator.next(); // return "L"
// # stringIterator.next(); // return "e"
// # stringIterator.next(); // return "e"
// # stringIterator.next(); // return "t"
// # stringIterator.next(); // return "C"
// # stringIterator.next(); // return "o"
// # stringIterator.hasNext(); // return True
// # stringIterator.next(); // return "d"
// # stringIterator.hasNext(); // return True
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= compressedString.length <= 1000
// # compressedString consists of lower-case an upper-case English letters and
// # digits.
// # The number of a single character repetitions in compressedString is in the
// # range [1, 10^9]
// # At most 100 calls will be made to next and hasNext.
// # 
// # 
// #
// 
// # lc-original code=start
// class StringIterator:
//     """
//     Interview explanation
//     =====================
// 
//     Restate the problem
//     -------------------
//     We are given a compressed string.  It is encoded as repeated groups:
// 
//         letter + positive integer count
// 
//     Example:
// 
//         "L1e2t1"
// 
//     represents:
// 
//         "Leet"
// 
//     We need implement an iterator with:
// 
//     * `next()`
//       Return the next uncompressed character, or `" "` if no character remains.
// 
//     * `hasNext()`
//       Return whether any uncompressed character remains.
// 
//     Important constraint
//     --------------------
//     A count can be as large as:
// 
//         10^9
// 
//     So we must not fully decompress the string.  A compressed segment like
//     `"a1000000000"` would require one billion characters if expanded.
// 
//     Key idea: lazy parsing
//     ----------------------
//     We only need to answer calls one character at a time.  Therefore, store:
// 
//     * `self.index`
//       Current parsing position in the compressed string.
// 
//     * `self.current_char`
//       The character for the active run.
// 
//     * `self.remaining`
//       How many copies of `current_char` are still available.
// 
//     When `remaining` becomes 0, parse the next compressed run.
// 
//     Data structure choice
//     ---------------------
//     We do not need a queue of all expanded characters.
// 
//     We also do not need to pre-parse every `(char, count)` pair, although that
//     would be acceptable for length <= 1000.  Lazy parsing is more memory-friendly
//     and demonstrates the important iterator design principle:
// 
//         consume only what is needed.
// 
//     Algorithm for parsing one run
//     -----------------------------
//     If `self.index` points at a letter:
// 
//     1. Read that letter as `current_char`.
//     2. Move `self.index` forward by one.
//     3. Read all following digits to build the count.
//     4. Set `self.remaining = count`.
// 
//     Example:
// 
//         compressedString = "a12B3"
// 
//         parse at index 0:
//             char = 'a'
//             digits = "12"
//             remaining = 12
//             index now points to 'B'
// 
//     Method behavior
//     ---------------
//     `hasNext()`:
// 
//     * If `remaining > 0`, return True.
//     * Otherwise, parse the next run if available.
//     * Return whether `remaining > 0`.
// 
//     `next()`:
// 
//     * First call `hasNext()` to make sure a current run exists.
//     * If not, return `" "`.
//     * Otherwise, decrement `remaining` and return `current_char`.
// 
//     Correctness proof
//     -----------------
//     Lemma 1: `_load_next_group` correctly loads the next compressed run.
//     It reads exactly one letter and then all consecutive digits following that
//     letter.  By the problem format, every run is represented by a letter followed
//     by its positive count, so the loaded character and count are exactly the next
//     run in the compressed string.
// 
//     Lemma 2: `hasNext()` returns True exactly when at least one uncompressed
//     character remains.
//     If `remaining > 0`, the active run still has characters, so True is correct.
//     If `remaining == 0`, `hasNext()` attempts to load the next run.  If loading
//     succeeds, a positive count is available; otherwise the compressed string has
//     been fully consumed.  Therefore the return value is exact.
// 
//     Lemma 3: `next()` returns the next character in uncompressed order whenever
//     one exists.
//     `next()` ensures a run is loaded using `hasNext()`.  The active run's
//     character is exactly the next uncompressed character, repeated
//     `remaining` times.  Returning it and decrementing `remaining` consumes one
//     copy, preserving iterator order.
// 
//     Theorem: The iterator behaves according to the specification.
//     By Lemma 2, `hasNext()` is correct.  By Lemma 3, `next()` returns each
//     uncompressed character in order, and when Lemma 2 says no character remains,
//     `next()` returns `" "`.  Thus both methods satisfy the required behavior.
// 
//     Complexity analysis
//     -------------------
//     Let:
// 
//         L = len(compressedString)
//         C = number of calls to next/hasNext
// 
//     Each compressed character/digit is parsed at most once across the lifetime
//     of the iterator.
// 
//     Constructor:
//         O(1) time, O(1) extra space
// 
//     `next()` / `hasNext()`:
//         O(1) amortized time
// 
//     Total parsing over all calls:
//         O(L)
// 
//     Space:
//         O(1)
// 
//     We store only the compressed string, an index, one active character, and one
//     remaining count.
// 
//     Edge cases
//     ----------
//     * Multi-digit counts:
//           "a12" must return 'a' twelve times.
// 
//     * Very large counts:
//           We store the count as an integer and decrement it; no expansion.
// 
//     * Calling `next()` after exhaustion:
//           Return a single space `" "`.
// 
//     * Repeated `hasNext()` calls:
//           They should not consume characters; this design only loads a run when
//           needed and does not decrement `remaining`.
// 
//     * Uppercase and lowercase letters:
//           Both are valid letters and are returned exactly as written.
// 
//     Test strategy
//     -------------
//     Useful tests:
// 
//     * Provided example:
//           "L1e2t1C1o1d1e1"
// 
//     * Multi-digit count:
//           "a12"
// 
//     * Exhaustion:
//           call `next()` more times than total expanded length.
// 
//     * Repeated `hasNext()` before `next()`.
// 
//     Possible improvement?
//     ---------------------
//     Pre-parsing all `(char, count)` pairs into a list is also valid and still
//     small for compressed length <= 1000.  Lazy parsing is slightly more elegant
//     for an iterator and avoids doing work for groups that may never be reached.
//     """
// 
//     def __init__(self, compressedString: str):
//         self.compressed = compressedString
//         self.index = 0
//         self.current_char = ""
//         self.remaining = 0
// 
//     def next(self) -> str:
//         if not self.hasNext():
//             return " "
// 
//         self.remaining -= 1
//         return self.current_char
// 
//     def hasNext(self) -> bool:
//         if self.remaining > 0:
//             return True
// 
//         self._load_next_group()
//         return self.remaining > 0
// 
//     def _load_next_group(self) -> None:
//         if self.index >= len(self.compressed):
//             return
// 
//         self.current_char = self.compressed[self.index]
//         self.index += 1
// 
//         count = 0
//         while self.index < len(self.compressed) and self.compressed[self.index].isdigit():
//             count = count * 10 + int(self.compressed[self.index])
//             self.index += 1
// 
//         self.remaining = count
// 
// 
// # Your StringIterator object will be instantiated and called as such:
// # obj = StringIterator(compressedString)
// # param_1 = obj.next()
// # param_2 = obj.hasNext()
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

class StringIterator {
    string compressed;
    int index = 0;
    char current = ' ';
    int remaining = 0;

    void loadNextGroup() {
        if (index >= (int)compressed.size()) return;
        current = compressed[index++];
        int count = 0;
        while (index < (int)compressed.size() && isdigit((unsigned char)compressed[index])) {
            count = count * 10 + compressed[index++] - '0';
        }
        remaining = count;
    }

public:
    StringIterator(string compressedString) : compressed(compressedString) {}

    char next() {
        if (!hasNext()) return ' ';
        --remaining;
        return current;
    }

    bool hasNext() {
        if (remaining > 0) return true;
        loadNextGroup();
        return remaining > 0;
    }
};
// @lc code=end
