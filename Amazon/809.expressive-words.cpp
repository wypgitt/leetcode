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
    vector<pair<char, int>> groups(const string& s) {
        vector<pair<char, int>> res;
        for (int i = 0; i < (int)s.size();) {
            int j = i + 1;
            while (j < (int)s.size() && s[j] == s[i]) ++j;
            res.push_back({s[i], j - i});
            i = j;
        }
        return res;
    }

public:
    int expressiveWords(string s, vector<string>& words) {
        auto target = groups(s);
        int ans = 0;
        for (const string& word : words) {
            auto g = groups(word);
            if (g.size() != target.size()) continue;
            bool ok = true;
            for (int i = 0; i < (int)g.size(); ++i) {
                if (g[i].first != target[i].first || g[i].second > target[i].second || (target[i].second < 3 && g[i].second != target[i].second)) {
                    ok = false;
                    break;
                }
            }
            ans += ok;
        }
        return ans;
    }
};

/*
Interview explanation:
Run-length encode s and each word. Characters must match group by group; a word group may be shorter only when the target group length is at least three.

C++ data structures: vector<pair<char,int>> stores compact character runs.

Edge cases: target runs of length 1 or 2 cannot be stretched, so counts must match exactly.

Complexity: O(total characters) time and O(number of groups) space per processed string.
*/
