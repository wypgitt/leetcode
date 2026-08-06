#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    bool isOneEditDistance(string s, string t) {
        /*
        Approach: ensure s is the shorter string. At the first mismatch, equal
        lengths require the remaining suffixes to match after one replacement;
        unequal lengths require s[i:] to match t[i+1:] after one insertion into
        s. If no mismatch occurs, the strings are one edit apart only when their
        lengths differ by exactly one.

        Complexity: O(n) time, O(1) extra space.
        */
        if (abs((int)s.size() - (int)t.size()) > 1) return false;
        if (s.size() > t.size()) swap(s, t);
        for (int i = 0; i < (int)s.size(); ++i) {
            if (s[i] == t[i]) continue;
            if (s.size() == t.size()) return s.substr(i + 1) == t.substr(i + 1);
            return s.substr(i) == t.substr(i + 1);
        }
        return t.size() - s.size() == 1;
    }
};
