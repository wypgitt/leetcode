#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    vector<bool> canMakePaliQueries(string s, vector<vector<int>>& queries) {
        vector<int> prefix(s.size() + 1, 0);
        for (int i = 0; i < (int)s.size(); ++i) {
            prefix[i + 1] = prefix[i] ^ (1 << (s[i] - 'a'));
        }

        vector<bool> answer;
        answer.reserve(queries.size());
        for (const auto& query : queries) {
            int left = query[0], right = query[1], k = query[2];
            int mask = prefix[right + 1] ^ prefix[left];
            int odd = __builtin_popcount((unsigned)mask);
            answer.push_back(odd / 2 <= k);
        }
        return answer;
    }
};

/*
Interview Explanation

Core idea:
A string can be rearranged into a palindrome if at most one character has odd
frequency. Replacing one character can fix two odd counts, so k replacements
can fix 2k odd characters.

C++ data structures:
- vector<int> prefix stores parity bitmasks. Bit b is 1 if that character has
  odd count in the prefix.
- XOR of two prefix masks gives parity for a substring.

Algorithm:
1. Build prefix parity masks.
2. For each query, compute substring mask with XOR.
3. Count odd-frequency characters using __builtin_popcount.
4. Return true if odd / 2 <= k.

Correctness:
Only parity matters for palindrome rearrangement. Each replacement can turn one
odd character into another needed character, reducing odd count by two. Thus a
substring is feasible exactly when half its odd count is at most k.

Complexity:
O(n + q) time and O(n) space.

Edge cases:
- Already-palindromic parity needs 0 replacements.
- One odd character also needs 0 replacements.
*/
