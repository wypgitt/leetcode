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
    string s;
    vector<int> ans;
    const long long LIMIT = INT_MAX;

    bool dfs(int pos) {
        if (pos == (int)s.size()) return ans.size() >= 3;
        long long value = 0;
        for (int end = pos; end < (int)s.size(); ++end) {
            if (end > pos && s[pos] == '0') break;
            value = value * 10 + s[end] - '0';
            if (value > LIMIT) break;
            if (ans.size() >= 2) {
                long long expected = (long long)ans[ans.size() - 1] + ans[ans.size() - 2];
                if (value < expected) continue;
                if (value > expected) break;
            }
            ans.push_back((int)value);
            if (dfs(end + 1)) return true;
            ans.pop_back();
        }
        return false;
    }

public:
    vector<int> splitIntoFibonacci(string num) {
        s = num;
        ans.clear();
        dfs(0);
        return ans;
    }
};

/*
Interview explanation:
Backtrack possible next numbers. Once two numbers exist, the next value is forced to their sum, so branches prune quickly.

C++ data structures: vector<int> stores the current sequence; long long checks overflow before casting to int.

Edge cases: leading zero is allowed only for the number 0; all values must fit in signed 32-bit range.

Complexity: effectively O(n^2) choices for the first two split points, with O(n) recursion/output space.
*/
