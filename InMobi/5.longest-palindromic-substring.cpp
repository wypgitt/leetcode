#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    string longestPalindrome(string s) {
        /*
        Approach:
        Every palindrome has a center: either one character for odd length or
        the gap between two characters for even length. Expand from each center
        while both sides match and keep the longest interval found.

        C++ notes:
        string::substr(start, length) returns the final answer copy.

        Complexity: O(n^2) time and O(1) extra space.
        */
        int bestStart = 0, bestLen = 0;
        auto expand = [&](int left, int right) {
            while (left >= 0 && right < (int)s.size() && s[left] == s[right]) {
                --left;
                ++right;
            }
            int len = right - left - 1;
            if (len > bestLen) {
                bestLen = len;
                bestStart = left + 1;
            }
        };
        for (int i = 0; i < (int)s.size(); ++i) {
            expand(i, i);
            expand(i, i + 1);
        }
        return s.substr(bestStart, bestLen);
    }
};
