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
    int lengthOfLongestSubstring(string s) {
        /*
        Approach:
        Use a sliding window [left, right] with no duplicate characters. last[c]
        stores the most recent index of c. When a repeated character appears
        inside the current window, move left just past its previous occurrence.

        C++ notes:
        vector<int> of size 256 works as an array map for byte-sized chars and is
        faster than unordered_map for ordinary LeetCode strings.

        Complexity: O(n) time and O(1) space.
        */
        vector<int> last(256, -1);
        int left = 0, best = 0;
        for (int right = 0; right < (int)s.size(); ++right) {
            unsigned char ch = static_cast<unsigned char>(s[right]);
            if (last[ch] >= left) left = last[ch] + 1;
            last[ch] = right;
            best = max(best, right - left + 1);
        }
        return best;
    }
};
