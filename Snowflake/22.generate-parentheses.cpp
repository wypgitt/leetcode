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
    vector<string> generateParenthesis(int n) {
        /*
        Approach:
        Backtrack all valid prefixes. Add '(' while fewer than n opens have been
        used. Add ')' only when it would not exceed the number of opens, keeping
        every prefix valid.

        Complexity: O(C_n * n) time and output space, O(n) recursion stack.
        */
        vector<string> ans;
        string path;
        function<void(int, int)> dfs = [&](int opened, int closed) {
            if ((int)path.size() == 2 * n) {
                ans.push_back(path);
                return;
            }
            if (opened < n) {
                path.push_back('(');
                dfs(opened + 1, closed);
                path.pop_back();
            }
            if (closed < opened) {
                path.push_back(')');
                dfs(opened, closed + 1);
                path.pop_back();
            }
        };
        dfs(0, 0);
        return ans;
    }
};
