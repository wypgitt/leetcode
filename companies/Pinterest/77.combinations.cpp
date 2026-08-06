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
    vector<vector<int>> combine(int n, int k) {
        /*
        Approach:
        Backtrack increasing numbers so every combination is built once. Prune
        the loop when there are not enough remaining numbers to fill k slots.

        Complexity: O(C(n,k) * k) time and O(k) recursion space excluding output.
        */
        vector<vector<int>> ans;
        vector<int> path;
        function<void(int)> dfs = [&](int start) {
            if ((int)path.size() == k) {
                ans.push_back(path);
                return;
            }
            int need = k - (int)path.size();
            for (int value = start; value <= n - need + 1; ++value) {
                path.push_back(value);
                dfs(value + 1);
                path.pop_back();
            }
        };
        dfs(1);
        return ans;
    }
};
