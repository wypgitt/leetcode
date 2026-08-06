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
    vector<string> findRepeatedDnaSequences(string s) {
        /*
        Approach: slide a length-10 window across the string. The first set
        records windows seen once; the second records windows seen at least
        twice so duplicates are returned only once.

        C++ notes: unordered_set<string> matches Python set behavior.
        Complexity: O(n) expected time, O(n) space; each window length is fixed.
        */
        unordered_set<string> seen, repeated;
        for (int i = 0; i + 10 <= (int)s.size(); ++i) {
            string window = s.substr(i, 10);
            if (seen.count(window)) repeated.insert(window);
            else seen.insert(window);
        }
        return vector<string>(repeated.begin(), repeated.end());
    }
};
