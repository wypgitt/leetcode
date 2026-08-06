#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    int minMutation(string startGene, string endGene, vector<string>& bank) {
        unordered_set<string> valid(bank.begin(), bank.end());
        if (!valid.count(endGene)) return -1;
        queue<pair<string, int>> q;
        unordered_set<string> seen;
        q.push({startGene, 0});
        seen.insert(startGene);
        string choices = "ACGT";
        while (!q.empty()) {
            auto [gene, steps] = q.front();
            q.pop();
            if (gene == endGene) return steps;
            for (int i = 0; i < (int)gene.size(); ++i) {
                char old = gene[i];
                for (char c : choices) {
                    if (c == old) continue;
                    gene[i] = c;
                    if (valid.count(gene) && !seen.count(gene)) {
                        seen.insert(gene);
                        q.push({gene, steps + 1});
                    }
                }
                gene[i] = old;
            }
        }
        return -1;
    }
};

/*
Interview explanation:
This is an unweighted shortest path over valid gene strings, so BFS returns the minimum number of mutations when endGene is first reached.

C++ data structures: unordered_set gives average O(1) membership for bank and visited genes; queue holds BFS states.

Edge cases: if endGene is absent from bank, no valid sequence can end there.

Complexity: O(B*L*4) time for B bank genes of length L=8, and O(B) space.
*/
