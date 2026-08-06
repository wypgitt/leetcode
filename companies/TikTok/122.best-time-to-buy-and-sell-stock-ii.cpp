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
    int maxProfit(vector<int>& prices) {
        /*
        Approach: every positive day-to-day price increase can be captured as a
        transaction. Summing those increases is equivalent to buying at each
        valley and selling at each following peak, but with simpler code.

        C++ notes: vector<int>& passes the price array without copying.
        Complexity: O(n) time, O(1) space.
        */
        int profit = 0;
        for (int i = 1; i < (int)prices.size(); ++i) {
            profit += max(0, prices[i] - prices[i - 1]);
        }
        return profit;
    }
};
