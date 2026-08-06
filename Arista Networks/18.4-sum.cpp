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
    vector<vector<int>> fourSum(vector<int>& nums, int target) {
        /*
        Approach:
        Sort the array, fix two non-duplicate anchors, then use two pointers for
        the remaining pair. long long is used for sums so large int inputs do not
        overflow while comparing to target.

        Complexity: O(n^3) time and O(log n) to O(n) sort stack space.
        */
        sort(nums.begin(), nums.end());
        vector<vector<int>> ans;
        int n = (int)nums.size();
        for (int i = 0; i < n - 3; ++i) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;
            for (int j = i + 1; j < n - 2; ++j) {
                if (j > i + 1 && nums[j] == nums[j - 1]) continue;
                int left = j + 1, right = n - 1;
                while (left < right) {
                    long long sum = (long long)nums[i] + nums[j] + nums[left] + nums[right];
                    if (sum == target) {
                        ans.push_back({nums[i], nums[j], nums[left], nums[right]});
                        int lv = nums[left], rv = nums[right];
                        while (left < right && nums[left] == lv) ++left;
                        while (left < right && nums[right] == rv) --right;
                    } else if (sum < target) {
                        ++left;
                    } else {
                        --right;
                    }
                }
            }
        }
        return ans;
    }
};
