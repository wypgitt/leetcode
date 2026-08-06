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
    int maximumGap(vector<int>& nums) {
        /*
        Approach: bucket by value range using the pigeonhole principle. The max
        gap cannot be inside a bucket when bucket size is chosen as ceil(range /
        (n-1)); it must be between the max of a non-empty bucket and the min of
        the next non-empty bucket.

        C++ notes: each Bucket stores whether it is used plus min/max values.
        Complexity: O(n) time, O(n) space.
        */
        int n = nums.size();
        if (n < 2) return 0;
        int lo = *min_element(nums.begin(), nums.end());
        int hi = *max_element(nums.begin(), nums.end());
        if (lo == hi) return 0;
        int size = max(1, (hi - lo + n - 2) / (n - 1));
        int count = (hi - lo) / size + 1;
        struct Bucket { bool used = false; int mn = INT_MAX; int mx = INT_MIN; };
        vector<Bucket> buckets(count);
        for (int num : nums) {
            int b = (num - lo) / size;
            buckets[b].used = true;
            buckets[b].mn = min(buckets[b].mn, num);
            buckets[b].mx = max(buckets[b].mx, num);
        }
        int best = 0, prevMax = lo;
        bool havePrev = false;
        for (const Bucket& bucket : buckets) {
            if (!bucket.used) continue;
            if (havePrev) best = max(best, bucket.mn - prevMax);
            prevMax = bucket.mx;
            havePrev = true;
        }
        return best;
    }
};
