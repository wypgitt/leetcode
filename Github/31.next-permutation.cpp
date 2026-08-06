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
    void nextPermutation(vector<int>& nums) {
        /*
        Approach:
        Find the first index from the right where nums[i] < nums[i+1]; this is
        the pivot before the longest non-increasing suffix. Swap it with the
        smallest larger value in the suffix, then reverse the suffix to make it
        the smallest possible order.

        Complexity: O(n) time and O(1) space.
        */
        int i = (int)nums.size() - 2;
        while (i >= 0 && nums[i] >= nums[i + 1]) --i;
        if (i >= 0) {
            int j = (int)nums.size() - 1;
            while (nums[j] <= nums[i]) --j;
            swap(nums[i], nums[j]);
        }
        reverse(nums.begin() + i + 1, nums.end());
    }
};
