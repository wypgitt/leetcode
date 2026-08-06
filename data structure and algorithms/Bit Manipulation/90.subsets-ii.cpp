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
    vector<vector<int>> subsetsWithDup(vector<int>& nums) {
        /*
        Approach:
        Sort so duplicates are adjacent. During backtracking, skip a duplicate
        if the previous equal value was not chosen at this same recursion depth;
        otherwise the same subset would be generated twice.

        Complexity: O(U*n) time where U is the number of unique subsets, O(n)
        recursion space excluding output.
        */
        sort(nums.begin(), nums.end());
        vector<vector<int>> ans;
        vector<int> path;
        function<void(int)> dfs = [&](int start) {
            ans.push_back(path);
            for (int i = start; i < (int)nums.size(); ++i) {
                if (i > start && nums[i] == nums[i - 1]) continue;
                path.push_back(nums[i]);
                dfs(i + 1);
                path.pop_back();
            }
        };
        dfs(0);
        return ans;
    }
};
