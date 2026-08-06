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
    int lowerBound(const vector<int>& nums, long long value) {
        int left = 0, right = (int)nums.size();
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] < value) left = mid + 1;
            else right = mid;
        }
        return left;
    }

public:
    vector<int> searchRange(vector<int>& nums, int target) {
        /*
        Approach:
        The first occurrence is lower_bound(target). The first index after the
        target run is lower_bound(target + 1), so the last occurrence is one
        before that. Validate that the first index really contains target.

        C++ notes:
        The helper implements lower_bound explicitly to mirror the Python binary
        search logic.

        Complexity: O(log n) time and O(1) space.
        */
        int first = lowerBound(nums, target);
        if (first == (int)nums.size() || nums[first] != target) return {-1, -1};
        int last = lowerBound(nums, (long long)target + 1) - 1;
        return {first, last};
    }
};
