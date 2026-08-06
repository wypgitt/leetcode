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
    void sortColors(vector<int>& nums) {
        /*
        Approach:
        Dutch National Flag partitioning. Maintain [0, low) as zeros, [low, mid)
        as ones, and (high, end] as twos. Inspect mid and swap into the correct
        region.

        Complexity: O(n) time and O(1) space.
        */
        int low = 0, mid = 0, high = (int)nums.size() - 1;
        while (mid <= high) {
            if (nums[mid] == 0) swap(nums[low++], nums[mid++]);
            else if (nums[mid] == 1) ++mid;
            else swap(nums[mid], nums[high--]);
        }
    }
};
