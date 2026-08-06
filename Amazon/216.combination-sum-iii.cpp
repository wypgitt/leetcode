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
    vector<vector<int>> combinationSum3(int k, int n) {
        /*
        Approach: backtrack increasing digits from 1 to 9, so each combination is
        generated once. Stop when k numbers are chosen and keep it only if the
        remaining sum is zero.

        Complexity: O(C(9,k) * k) time, O(k) recursion space excluding output.
        */
        vector<vector<int>> ans;
        vector<int> path;
        function<void(int, int)> dfs = [&](int start, int remaining) {
            if ((int)path.size() == k) {
                if (remaining == 0) ans.push_back(path);
                return;
            }
            int need = k - path.size();
            for (int num = start; num <= 9; ++num) {
                if (num > remaining) break;
                if (10 - num < need) break;
                path.push_back(num);
                dfs(num + 1, remaining - num);
                path.pop_back();
            }
        };
        dfs(1, n);
        return ans;
    }
};
