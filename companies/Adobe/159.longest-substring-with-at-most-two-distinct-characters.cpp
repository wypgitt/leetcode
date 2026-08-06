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
    int lengthOfLongestSubstringTwoDistinct(string s) {
        /*
        Approach: sliding window with character counts. Expand right, and while
        more than two distinct characters are present, shrink from the left until
        the window is valid again.

        C++ notes: unordered_map<char,int> mirrors Python defaultdict(int).
        Complexity: O(n) time, O(1) space because at most character-set size.
        */
        unordered_map<char,int> counts;
        int left = 0, best = 0;
        for (int right = 0; right < (int)s.size(); ++right) {
            ++counts[s[right]];
            while (counts.size() > 2) {
                char old = s[left++];
                if (--counts[old] == 0) counts.erase(old);
            }
            best = max(best, right - left + 1);
        }
        return best;
    }
};
