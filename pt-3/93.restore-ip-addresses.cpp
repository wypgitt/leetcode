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
    vector<string> restoreIpAddresses(string s) {
        /*
        Approach:
        Backtrack exactly four segments. Each segment has length 1..3, no
        leading zero unless it is "0", and integer value at most 255. Prune when
        remaining characters cannot fill the remaining segment count.

        Complexity: O(1) in practice because at most 3^4 segment choices exist;
        output size is bounded.
        */
        vector<string> ans, path;
        auto valid = [](const string& part) {
            if (part.size() > 1 && part[0] == '0') return false;
            return stoi(part) <= 255;
        };
        function<void(int)> dfs = [&](int index) {
            int partsLeft = 4 - (int)path.size();
            int charsLeft = (int)s.size() - index;
            if (charsLeft < partsLeft || charsLeft > partsLeft * 3) return;
            if (path.size() == 4) {
                if (index == (int)s.size()) ans.push_back(path[0] + "." + path[1] + "." + path[2] + "." + path[3]);
                return;
            }
            for (int end = index + 1; end <= min(index + 3, (int)s.size()); ++end) {
                string part = s.substr(index, end - index);
                if (valid(part)) {
                    path.push_back(part);
                    dfs(end);
                    path.pop_back();
                }
            }
        };
        dfs(0);
        return ans;
    }
};
