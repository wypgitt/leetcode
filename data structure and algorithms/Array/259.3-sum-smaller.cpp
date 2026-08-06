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
    int threeSumSmaller(vector<int>& nums, int target) {
        /*
        Approach: sort, fix one index, then use two pointers. If nums[i] +
        nums[left] + nums[right] is smaller than target, then every index between
        left and right paired with left also works, contributing right-left
        triplets.

        Complexity: O(n^2) time, O(log n) to O(n) sorting stack space.
        */
        sort(nums.begin(), nums.end());
        int count = 0;
        for (int i = 0; i < (int)nums.size() - 2; ++i) {
            int left = i + 1, right = nums.size() - 1;
            while (left < right) {
                if (nums[i] + nums[left] + nums[right] < target) {
                    count += right - left;
                    ++left;
                } else {
                    --right;
                }
            }
        }
        return count;
    }
};
