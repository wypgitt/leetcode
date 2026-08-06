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
    vector<vector<int>> permuteUnique(vector<int>& nums) {
        /*
        Approach:
        Sort nums so equal values are adjacent. During backtracking, skip nums[i]
        if it equals nums[i-1] and the previous equal value has not been used in
        this position; that prevents duplicate permutations.

        Complexity: O(U * n) time where U is unique permutations, O(n) stack.
        */
        sort(nums.begin(), nums.end());
        vector<vector<int>> ans;
        vector<int> path;
        vector<bool> used(nums.size(), false);
        function<void()> dfs = [&]() {
            if (path.size() == nums.size()) {
                ans.push_back(path);
                return;
            }
            for (int i = 0; i < (int)nums.size(); ++i) {
                if (used[i]) continue;
                if (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) continue;
                used[i] = true;
                path.push_back(nums[i]);
                dfs();
                path.pop_back();
                used[i] = false;
            }
        };
        dfs();
        return ans;
    }
};
