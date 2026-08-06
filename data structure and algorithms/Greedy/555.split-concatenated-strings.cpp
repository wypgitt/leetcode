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
    string splitLoopedString(vector<string>& strs) {
        vector<string> parts;
        for (string s : strs) {
            string r = s;
            reverse(r.begin(), r.end());
            parts.push_back(max(s, r));
        }
        string best;
        int n = strs.size();
        for (int i = 0; i < n; ++i) {
            string middle;
            for (int j = i + 1; j < n; ++j) middle += parts[j];
            for (int j = 0; j < i; ++j) middle += parts[j];
            vector<string> options = {strs[i], string(strs[i].rbegin(), strs[i].rend())};
            for (const string& cur : options) {
                for (int cut = 0; cut < (int)cur.size(); ++cut) {
                    string cand = cur.substr(cut) + middle + cur.substr(0, cut);
                    best = max(best, cand);
                }
            }
        }
        return best;
    }
};

/*
Interview explanation:
All strings not crossing the final split can independently take their lexicographically larger orientation. The boundary string must be tried in both orientations and all cut positions.

C++ data structures: vector<string> stores chosen orientations; string substrings construct candidates.

Edge cases: using only the boundary string's larger orientation can miss the optimum, so both are tested.

Complexity: O(L^2) candidate construction in the worst case, accepted for constraints; O(L) extra space per candidate.
*/
