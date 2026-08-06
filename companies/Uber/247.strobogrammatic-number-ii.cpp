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
    vector<string> findStrobogrammatic(int n) {
        /*
        Approach: recursively build from the inside out. For each inner string,
        wrap it with valid rotated digit pairs. Skip leading zero pairs at the
        outermost level.

        Complexity: O(5^(n/2) * n) time and output space.
        */
        vector<pair<char,char>> pairs = {{'0','0'}, {'1','1'}, {'6','9'}, {'8','8'}, {'9','6'}};
        function<vector<string>(int, int)> build = [&](int length, int total) -> vector<string> {
            if (length == 0) return {""};
            if (length == 1) return {"0", "1", "8"};
            vector<string> ans;
            for (const string& inner : build(length - 2, total)) {
                for (auto [a, b] : pairs) {
                    if (length == total && a == '0') continue;
                    ans.push_back(string(1, a) + inner + string(1, b));
                }
            }
            return ans;
        };
        return build(n, n);
    }
};
