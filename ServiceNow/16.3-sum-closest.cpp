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
    int threeSumClosest(vector<int>& nums, int target) {
        /*
        Approach:
        Sort, fix one value, then scan the remaining range with two pointers.
        Move left/right based on whether the current sum is too small or too
        large. Track the sum with minimum absolute distance to target.

        Complexity: O(n^2) time and O(log n) to O(n) sorting stack space.
        */
        sort(nums.begin(), nums.end());
        int best = nums[0] + nums[1] + nums[2];
        for (int i = 0; i < (int)nums.size() - 2; ++i) {
            int left = i + 1, right = (int)nums.size() - 1;
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                if (abs((long long)target - sum) < abs((long long)target - best)) best = sum;
                if (sum == target) return target;
                if (sum < target) ++left;
                else --right;
            }
        }
        return best;
    }
};
