#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    int findSubstringInWraproundString(string s) {
        vector<int> best(26, 0);
        int run = 0;
        char prev = 0;
        for (char c : s) {
            if (prev && (c - prev + 26) % 26 == 1) ++run;
            else run = 1;
            best[c - 'a'] = max(best[c - 'a'], run);
            prev = c;
        }
        return accumulate(best.begin(), best.end(), 0);
    }
};

/*
Interview explanation:
For each ending letter, only the longest valid wraparound substring ending there matters. It contributes all shorter suffix lengths ending at that letter without duplicates.

C++ data structures: a fixed vector<int> of size 26 stores maximum run lengths.

Edge cases: z->a is valid through modulo arithmetic; breaks reset the run to 1.

Complexity: O(n) time and O(1) space.
*/
