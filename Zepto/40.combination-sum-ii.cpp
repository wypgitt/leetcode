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
    vector<vector<int>> combinationSum2(vector<int>& candidates, int target) {
        /*
        Approach:
        Sort candidates so duplicates are adjacent. Backtracking advances to
        i+1 because each number can be used once. At the same recursion depth,
        skip equal values after the first to avoid duplicate combinations.

        Complexity: O(2^n * n) worst-case time including copies, O(n) stack.
        */
        sort(candidates.begin(), candidates.end());
        vector<vector<int>> ans;
        vector<int> path;
        function<void(int, int)> dfs = [&](int start, int remain) {
            if (remain == 0) {
                ans.push_back(path);
                return;
            }
            for (int i = start; i < (int)candidates.size() && candidates[i] <= remain; ++i) {
                if (i > start && candidates[i] == candidates[i - 1]) continue;
                path.push_back(candidates[i]);
                dfs(i + 1, remain - candidates[i]);
                path.pop_back();
            }
        };
        dfs(0, target);
        return ans;
    }
};
