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
    int shortestWordDistance(vector<string>& wordsDict, string word1, string word2) {
        /*
        Approach: if the words are equal, track the previous occurrence of that
        same word and minimize adjacent occurrence gaps. Otherwise track the last
        seen index of each word and update the answer whenever the other has been
        seen.

        Complexity: O(n) time, O(1) space.
        */
        int best = INT_MAX;
        if (word1 == word2) {
            int prev = -1;
            for (int i = 0; i < (int)wordsDict.size(); ++i) {
                if (wordsDict[i] == word1) {
                    if (prev != -1) best = min(best, i - prev);
                    prev = i;
                }
            }
            return best;
        }
        int last1 = -1, last2 = -1;
        for (int i = 0; i < (int)wordsDict.size(); ++i) {
            if (wordsDict[i] == word1) {
                last1 = i;
                if (last2 != -1) best = min(best, abs(last1 - last2));
            } else if (wordsDict[i] == word2) {
                last2 = i;
                if (last1 != -1) best = min(best, abs(last1 - last2));
            }
        }
        return best;
    }
};
