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
    vector<int> majorityElement(vector<int>& nums) {
        /*
        Approach: Boyer-Moore generalized for elements appearing more than n/3.
        There can be at most two such elements, so maintain two candidates and
        counters, then verify them with a second pass.

        Complexity: O(n) time, O(1) space.
        */
        int cand1 = 0, cand2 = 1, count1 = 0, count2 = 0;
        for (int num : nums) {
            if (num == cand1) ++count1;
            else if (num == cand2) ++count2;
            else if (count1 == 0) { cand1 = num; count1 = 1; }
            else if (count2 == 0) { cand2 = num; count2 = 1; }
            else { --count1; --count2; }
        }
        vector<int> ans;
        count1 = count2 = 0;
        for (int num : nums) {
            if (num == cand1) ++count1;
            else if (num == cand2) ++count2;
        }
        if (count1 > (int)nums.size() / 3) ans.push_back(cand1);
        if (count2 > (int)nums.size() / 3) ans.push_back(cand2);
        return ans;
    }
};
