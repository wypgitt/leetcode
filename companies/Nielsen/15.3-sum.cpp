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
    vector<vector<int>> threeSum(vector<int>& nums) {
        /*
        Approach:
        Sort the array. For each non-duplicate anchor, use two pointers to find
        pairs whose sum is the negative anchor. Skip duplicate anchors and pair
        values so each triplet appears once.

        C++ notes:
        vector<vector<int>> is the natural equivalent of Python list[list[int]].

        Complexity: O(n^2) time and O(log n) to O(n) sort stack space.
        */
        sort(nums.begin(), nums.end());
        vector<vector<int>> ans;
        int n = (int)nums.size();
        for (int i = 0; i < n - 2; ++i) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;
            int left = i + 1, right = n - 1;
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                if (sum == 0) {
                    ans.push_back({nums[i], nums[left], nums[right]});
                    int lv = nums[left], rv = nums[right];
                    while (left < right && nums[left] == lv) ++left;
                    while (left < right && nums[right] == rv) --right;
                } else if (sum < 0) {
                    ++left;
                } else {
                    --right;
                }
            }
        }
        return ans;
    }
};
