package main

import (
	"strconv"
	"strings"
)

type parsedTransaction struct {
	name   string
	time   int
	amount int
	city   string
}

func invalidTransactions(transactions []string) []string {
	parsed := make([]parsedTransaction, len(transactions))
	byName := map[string][]int{}
	invalid := make([]bool, len(transactions))

	for i, transaction := range transactions {
		parts := strings.Split(transaction, ",")
		time, _ := strconv.Atoi(parts[1])
		amount, _ := strconv.Atoi(parts[2])
		parsed[i] = parsedTransaction{name: parts[0], time: time, amount: amount, city: parts[3]}
		byName[parts[0]] = append(byName[parts[0]], i)
		if amount > 1000 {
			invalid[i] = true
		}
	}

	for _, indices := range byName {
		for i := 0; i < len(indices); i++ {
			for j := i + 1; j < len(indices); j++ {
				a, b := parsed[indices[i]], parsed[indices[j]]
				diff := a.time - b.time
				if diff < 0 {
					diff = -diff
				}
				if diff <= 60 && a.city != b.city {
					invalid[indices[i]] = true
					invalid[indices[j]] = true
				}
			}
		}
	}

	answer := []string{}
	for i, transaction := range transactions {
		if invalid[i] {
			answer = append(answer, transaction)
		}
	}
	return answer
}

