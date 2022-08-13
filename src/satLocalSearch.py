class SatLocalSearch:
    def __init__(self, file):

        self.literals = {}
        self.clauses = []
        self.result = None
        self.unsat = 0
        self.history = []
        
        for line in open(file).read().split('\n'):
            line = line.split()
            for var in line:
                # let there exist literal called '-'
                if var[0] == '-' and len(var) != 1:
                    self.literals[var[1:]] = 0
                else:
                    self.literals[var] = 1
            if line != []:
                self.clauses.append(line)

        try:
            self.__computeUnitClausesAndSimplify()  # do simplification and check for unsat
        except:
            print('COLLISION: unsat')
            self.unsat = 1

    def __computeUnitClausesAndSimplify(self) -> None:
        hardCoded = {}
        for line in list(self.clauses):
            if len(line) == 1:
                if line[0][0] == '-':
                    if line[0][1:] in hardCoded and hardCoded[line[0][1:]] == 1:
                        raise Collision()

                    hardCoded[line[0][1:]] = 0
                    try:
                        self.literals.pop(line[0][1:])
                    except:
                        pass
                else:
                    if line[0] in hardCoded and hardCoded[line[0]] == 0:
                        raise Collision()

                    hardCoded[line[0]] = 1
                    try:
                        self.literals.pop(line[0])
                    except:
                        pass
                self.clauses.remove(line)
        if len(hardCoded) != 0:
            self.__simplifyClauses(hardCoded)

    def __simplifyClauses(self, alone) -> None:
        replace = list(self.clauses)
        self.clauses = []
        for cl in replace:
            addMe = 1
            for var in cl:

                if len(var) == 2 and var[1:] in alone:
                    if alone[var[1:]] == 1:
                        cl.remove(var)
                    else:
                        addMe = 0  # useless clause because it would be true either way
                        break

                elif len(var) == 1 and var in alone:
                    if alone[var] == 1:
                        addMe = 0
                        break
                    else:
                        cl.remove(var)

            if addMe:
                self.clauses.append(cl)

        self.__computeUnitClausesAndSimplify()
        self.literals.update(alone)

    def __checkClause(self, cl):
        for var in cl:
            if len(var) == 2 and self.literals[var[1:]] == 0:
                return 1
            elif len(var) == 2 and self.literals[var[1:]] == -1:
                return var
            elif len(var) == 1 and self.literals[var] == 1:
                return 1
            elif len(var) == 1 and self.literals[var] == -1:
                return var
        return 0

    def __solutionCheck(self):
        for allVars in self.clauses:
            test = self.__checkClause(allVars)
            if test != 1:
                return (test, allVars)
        return 1

    def __countSatisfiedClauses(self) -> int:
        counter = 0
        for i in self.clauses:
            if self.__checkClause(i) == 1:
                counter += 1
        return counter

    def __flipBit(self, i) -> None:
        self.literals[i] = 1 if self.literals[i] == 0 else 0

    def __findBest(self):
        initialSatisfied = self.__countSatisfiedClauses()
        bestChoices = []
        for i in self.literals: # could be improved by iterating through non-already used literals.

            self.__flipBit(i)

            if self.__solutionCheck() == 1:
                self.__flipBit(i)
                # return position to flip where a solution is guaranteed
                return [(333, i)]

            newSatisfied = self.__countSatisfiedClauses()
            self.__flipBit(i)
            difference = newSatisfied - initialSatisfied

            if len(bestChoices) == 0 or difference > bestChoices[0][0]:
                bestChoices = [(difference, i)]

            elif difference == bestChoices[0][0]:
                bestChoices += [(difference, i)]
        return bestChoices if len(bestChoices) != 0 else None

    def __weKnow(self, solution) -> None:
        print('SAT: [', ', '.join([x + ' = ' + str(solution[x])
                                   for x in self.literals if solution[x] != -1]) + ' ]')

    def __main(self, vals, flip):

        if self.__solutionCheck() != 1:
            arrOfBitFlips = self.__findBest()
            # history has every bit flip tried
            while len(arrOfBitFlips) > 0 and arrOfBitFlips[0][1] in self.history:
                # I do not have demonstration for why this works in CNF, but I cannot find a counterexample so for now, trust me.
                # Check this out: This way we force the solver to try different routes in the search space and not take a longer path towards the goal 
                # there cannot be a cycle with new satisfied clauses != 0
                arrOfBitFlips.pop(0)

            if len(self.history) == 55:  # 50 is arbitrary and should be (number of literals) * 2 - 2 (based on my calculations)
                self.history.pop(0)
            if arrOfBitFlips == None:
                return None

            for flip in arrOfBitFlips:
                self.history.append(flip[1])
                self.__flipBit(flip[1])

                if self.__solutionCheck() == 1:  # could be removed
                    return vals                #

                if self.__main(vals, flip) != None:
                    return vals
        else:
            return vals

    def check(self, printt=1) -> None:
        if not self.unsat:
            solution = self.__main(self.literals, 0)
            if solution:
                self.result = solution
                if printt:
                    print('sat')

                return

        print('unsat')
        self.unsat = 1

    def model(self):
        if self.result == None:
            self.check(0)
        if not self.unsat:
            self.__weKnow(self.result)


if __name__ == "__main__":
    SatLocalSearch('input.txt').model()
