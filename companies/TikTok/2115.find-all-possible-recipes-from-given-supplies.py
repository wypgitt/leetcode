#
# @lc app=leetcode id=2115 lang=python3
#
# [2115] Find All Possible Recipes from Given Supplies
#
# https://leetcode.com/problems/find-all-possible-recipes-from-given-supplies/description/
#
# algorithms
# Medium (57.06%)
# Likes:    2713
# Dislikes: 143
# Total Accepted:    242K
# Total Submissions: 424.1K
# Testcase Example:  "[\"bread\"]\n[[\"yeast\",\"flour\"]]\n[\"yeast\",\"flour\",\"corn\"]"
#
# You have information about n different recipes. You are given a string array
# recipes and a 2D string array ingredients. The i^th recipe has the name
# recipes[i], and you can create it if you have all the needed ingredients from
# ingredients[i]. A recipe can also be an ingredient for other recipes, i.e.,
# ingredients[i] may contain a string that is in recipes.
#
# You are also given a string array supplies containing all the ingredients that
# you initially have, and you have an infinite supply of all of them.
#
# Return a list of all the recipes that you can create. You may return the
# answer in any order.
#
# Note that two recipes may contain each other in their ingredients.
#
#
#
# Example 1:
#
# Input: recipes = ["bread"], ingredients = [["yeast","flour"]], supplies =
# ["yeast","flour","corn"]
# Output: ["bread"]
# Explanation:
# We can create "bread" since we have the ingredients "yeast" and "flour".
#
# Example 2:
#
# Input: recipes = ["bread","sandwich"], ingredients =
# [["yeast","flour"],["bread","meat"]], supplies = ["yeast","flour","meat"]
# Output: ["bread","sandwich"]
# Explanation:
# We can create "bread" since we have the ingredients "yeast" and "flour".
# We can create "sandwich" since we have the ingredient "meat" and can create
# the ingredient "bread".
#
# Example 3:
#
# Input: recipes = ["bread","sandwich","burger"], ingredients =
# [["yeast","flour"],["bread","meat"],["sandwich","meat","bread"]], supplies =
# ["yeast","flour","meat"]
# Output: ["bread","sandwich","burger"]
# Explanation:
# We can create "bread" since we have the ingredients "yeast" and "flour".
# We can create "sandwich" since we have the ingredient "meat" and can create
# the ingredient "bread".
# We can create "burger" since we have the ingredient "meat" and can create the
# ingredients "bread" and "sandwich".
#
#
#
# Constraints:
#
#
# n == recipes.length == ingredients.length
#
#
# 1 <= n <= 100
#
#
# 1 <= ingredients[i].length, supplies.length <= 100
#
#
# 1 <= recipes[i].length, ingredients[i][j].length, supplies[k].length <= 10
#
#
# recipes[i], ingredients[i][j], and supplies[k] consist only of lowercase
# English letters.
#
#
# All the values of recipes and supplies combined are unique.
#
#
# Each ingredients[i] does not contain any duplicate values.
#


# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def findAllRecipes(
        self,
        recipes: List[str],
        ingredients: List[List[str]],
        supplies: List[str],
    ) -> List[str]:
        """
        Interview explanation:
        Recipes form a dependency graph on ingredients/recipes. Start from
        supplies; cook any recipe whose ingredients are all available.

        Algorithm:
        - Build graph: ingredient → recipes that need it; indegree per recipe.
        - BFS from supplies; when indegree hits 0, recipe is cookable and becomes supply.

        Complexity: O(n + e) time/space.
        """
        need = defaultdict(list)
        indeg = {}
        for r, ings in zip(recipes, ingredients):
            indeg[r] = len(ings)
            for ing in ings:
                need[ing].append(r)
        q = deque(supplies)
        ans = []
        while q:
            item = q.popleft()
            for r in need[item]:
                indeg[r] -= 1
                if indeg[r] == 0:
                    ans.append(r)
                    q.append(r)
        return ans

    def findAllRecipes_dfs(
        self,
        recipes: List[str],
        ingredients: List[List[str]],
        supplies: List[str],
    ) -> List[str]:
        """
        Interview explanation:
        Alternate DFS with memo: a recipe is makeable if all ingredients are
        supplies or makeable recipes (detect cycles as fail).

        Algorithm:
        - Map recipe→ingredients; DFS with 3-color / memo states.

        Complexity: O(n + e) time/space.
        """
        recipe_ing = dict(zip(recipes, ingredients))
        have = set(supplies)
        memo = {}

        def can(name: str, visiting: set) -> bool:
            if name in have:
                return True
            if name not in recipe_ing:
                return False
            if name in memo:
                return memo[name]
            if name in visiting:
                return False
            visiting.add(name)
            ok = all(can(ing, visiting) for ing in recipe_ing[name])
            visiting.remove(name)
            memo[name] = ok
            if ok:
                have.add(name)
            return ok

        return [r for r in recipes if can(r, set())]
# @lc code=end

