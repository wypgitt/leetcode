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
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        /*
        Approach:
        Sort candidates and backtrack from a start index. Reusing the same
        candidate is allowed, so the recursive call keeps i as the next start.
        Stop a loop early once the candidate exceeds the remaining target.

        Complexity: Exponential output-sensitive time, O(target/min candidate)
        recursion depth excluding output.
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
                path.push_back(candidates[i]);
                dfs(i, remain - candidates[i]);
                path.pop_back();
            }
        };
        dfs(0, target);
        return ans;
    }
};
