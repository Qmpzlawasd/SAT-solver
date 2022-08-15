from copy import deepcopy


class SatLookAhead:
    def __init__(self, file: str):

        self.literals = {}
        self.clauses = []
        self.result = None
        self.unsat = 0
        self.__mode = 1
        for line in open(file).read().split('\n'):
            line = line.split()
            for var in line:
                # let there exist literal called '-'
                if var[0] == '-' and len(var) != 1:
                    self.literals[var[1:]] = -1
                else:
                    self.literals[var] = -1

            if line != []:
                self.clauses.append(line)

        try:
            # do simplification and check for unsat
            self.__simplifyAutarky()
            self.__compute1SAT()
            if self.__solutionCheck(self.clauses, self.literals) == 1:
                self.result = self.literals
        except:
            print('COLLISION: unsat')
            self.unsat = 1

    def __simplifyAutarky(self) -> None:
        findAutarky = self.literals.copy()

        for cl in self.clauses:
            for var in cl:

                if len(var) == 2:
                    var = var[1:]
                    if var in findAutarky:
                        if findAutarky[var] == -1:
                            findAutarky[var] = 0
                        elif findAutarky[var] == 0:
                            findAutarky[var] = 0

                        else:
                            findAutarky.pop(var)

                elif len(var) == 1:
                    if var in findAutarky:
                        if findAutarky[var] == -1:
                            findAutarky[var] = 1
                        elif findAutarky[var] == 1:
                            findAutarky[var] = 1
                        else:
                            findAutarky.pop(var)

        for maybe in findAutarky:
            for cl in self.clauses.copy():
                if maybe in cl or f'-{maybe}' in cl:
                    self.clauses.remove(cl)
                    self.literals[maybe] = findAutarky[maybe]

    def __compute1SAT(self) -> None:

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
            self.__simplify1SAT(hardCoded)

    def __simplify1SAT(self, alone: dict) -> None:
        repl = list(self.clauses)
        self.clauses = []
        for cl in repl:
            addMe = 1
            for var in cl:

                if len(var) == 2:
                    var = var[1:]
                    if var in alone:
                        if alone[var] == 1:
                            cl.remove(f'-{var}')
                        else:
                            addMe = 0  # useless clause because it would be true either way
                            break

                elif len(var) == 1:
                    if var in alone:
                        if alone[var] == 1:
                            addMe = 0
                            break
                        else:
                            cl.remove(var)

            if addMe:
                self.clauses.append(cl)

        findAutarky = {}
        self.literals.update(alone)
        self.__compute1SAT()

    def __weKnow(self, solution: dict) -> None:
        print('SAT: [', ', '.join([x + ' = ' + str(solution[x]) if solution[x] != -1 else x + ' = *'
                                   for x in self.literals]) + ' ]')

    def __literalIsNegIn(self, target: chr, clauses: list):
        return [i for i in range(len(clauses)) if target == clauses[i][1:]]

    def __literalIsPosIn(self, target: chr, clauses: list):
        return [i for i in range(len(clauses)) if target == clauses[i]]

    def __satisfy(self, cl: list, sol: dict):

        ret = (-1, -1)
        for var in cl:
            if len(var) == 2 and sol[var[1:]] == 0:
                return True
            if len(var) == 1 and sol[var] == 1:
                return True

            if len(var) == 2 and sol[var[1:]] == -1 and ret == (-1, -1):
                ret = (var[1:], 0)
            elif ret != (-1, -1) and len(var) == 2 and sol[var[1:]] == -1:
                return True

            if len(var) == 1 and sol[var] == -1 and ret == (-1, -1):
                ret = (var, 1)
            elif len(var) == 1 and sol[var] == -1 and ret != (-1, -1):
                return True
        if ret[1] == 0:
            sol[ret[0]] = 0
            return ret[0]

        else:
            sol[ret[0]] = 1
            return ret[0]

        return True

    def __collectStatistics(self, oldClau: list, newClau: list, vals={}) -> int:
        if self.__mode == 1:  # nr of discovered placeholders
            return sum([1 if vals[var] != -1 else 0 for var in vals])

        if self.__mode == 2:  # nr of reduced equations
            return len(oldClau)-len(newClau)

        if self.__mode == 3:  # tho, this works best according to some non-mine research if we add weights and mark some equations as !important
            return sum([0 if i in oldClau else 1 for i in newClau])

    def __simplifyClauses(self,  clauses: list, alone: dict) -> int:
        repl = deepcopy(clauses)
        clauses.clear()
        goDeeper = 0
        for cl in repl:
            addMe = 1
            for var in cl:
                if len(cl) == 1:
                    addMe = 0
                    goDeeper = 1

                    if len(var) == 1 and alone[var] == -1:
                        alone[var] = 1

                    elif len(var) == 2 and alone[var[1:]] == -1:
                        alone[var[1:]] = 0
                    else:
                        addMe = 1  # PANIC
                        goDeeper = 0
                    break
                if len(var) == 2 and var[1:] in alone:
                    if alone[var[1:]] != -1:
                        if alone[var[1:]] == 1:
                            cl.remove(var)
                            goDeeper = 1
                        else:
                            addMe = 0
                            break

                elif len(var) == 1 and var in alone:
                    if alone[var] != -1:

                        if alone[var] == 1:
                            addMe = 0
                            break
                        else:
                            goDeeper = 1

                            cl.remove(var)
            if addMe:
                clauses.append(cl)
        if goDeeper:
            self.__simplifyClauses(clauses, alone)

        return len(clauses)

    def __solutionCheck(self, clauses: list, sol: dict):
        for allVars in clauses:
            test = self.__checkClause(allVars, sol)
            if test != 1:
                return test
        return 1

    def __checkClause(self, cl: list, sol: dict):
        for var in cl:
            if len(var) == 2 and sol[var[1:]] == 0:
                return 1
            elif len(var) == 2 and sol[var[1:]] == -1:
                return var
            elif len(var) == 1 and sol[var] == 1:
                return 1
            elif len(var) == 1 and sol[var] == -1:
                return var
        return 0

    def __find2SAT(self, variables, equations: list) -> list:
        twoSat = []
        neg = 0
        pos = 0

        for orLine in equations:
            if neg == 0 and ((len(orLine) == 2 and self.__literalIsNegIn(variables, orLine) != [])):
                twoSat.append(orLine)
                neg = 1
            elif pos == 0 and (len(orLine) == 2 and self.__literalIsPosIn(variables, orLine) != []):
                pos = 1  # is pos
                twoSat.append(orLine)
        return twoSat

    def __unitPropagation(self, liet: chr, cla: list, ll: dict) -> list:
        ret = []
        for cl in self.__find2SAT(liet, cla):
            newcla = cla.copy()
            newll = ll.copy()
            newcla.remove(cl)
            if newll[liet] == -1:
                if self.__literalIsNegIn(liet, cl) == []:
                    newll[liet] = 0

                else:
                    newll[liet] = 1

            self.__satisfy(cl, newll)  # infer neighbour

            self.__simplifyClauses(newcla, newll)  # let the magic begin

            if self.__solutionCheck(newcla, newll) == 1:
                return newll

            ret.append(  # return all work done
                (liet, newll[liet], self.__collectStatistics(cla, newcla, newll), newcla))

        return ret

    def __callToCompute(self, i: chr, cla: list, liter: dict):
        if self.__mode == 1:
            return self.__unitPropagation(
                i,  deepcopy(cla), deepcopy(liter))

        vrai = cla.copy()
        fals = cla.copy()

        if self.__mode == 2:
            liter[i] = 1
            diffTrue = len(cla) - self.__simplifyClauses(vrai, liter)

            liter[i] = 0
            diffFalse = len(cla) - self.__simplifyClauses(fals, liter)

        if self.__mode == 3:
            liter[i] = 1
            self.__simplifyClauses(vrai, liter)

            liter[i] = 0
            self.__simplifyClauses(fals, liter)

            diffFalse = self.__collectStatistics(cla, fals)
            diffTrue = self.__collectStatistics(cla, vrai)

        if diffFalse < diffTrue:
            liter[i] = 1
            fals = vrai
        return [(i, liter[i], max(diffFalse, diffTrue), fals)]

    def __main(self, cla: list, defLiterals: dict):
        top = ('', -1, -1)
        nonlit = [notLearnedYet for notLearnedYet in defLiterals if defLiterals[notLearnedYet] == -1]
        for i in nonlit:
            res = self.__callToCompute(i, cla, defLiterals)
            if isinstance(res, dict):
                return res

            for tup in res:
                if top[2] < tup[2]:
                    top = tup

        if top != ('', -1, -1):
            defLiterals[top[0]] = top[1]
            self.__simplifyClauses(cla, defLiterals)

            __main = self.__main(deepcopy(top[3]), deepcopy(defLiterals))
            if isinstance(__main, dict):
                return __main

        else:

            self.__simplifyClauses(cla, defLiterals)
            if cla == []:
                if self.__solutionCheck(cla, defLiterals) == 1:
                    return defLiterals
                else:
                    return None

            tryCla = self.__pickEquation(cla, defLiterals)
            if tryCla == None:
                return None
            varToSet = self.__checkClause(tryCla, defLiterals)

            if varToSet == 0:
                return None

            self.guideVarToTheTruth(varToSet, defLiterals)

            mainRet= self.__main(deepcopy(cla), deepcopy(defLiterals))
            if isinstance(__main, dict):
                return mainRet
            else:
                self.__flipBit(varToSet, defLiterals)
                self.__simplifyClauses(cla, defLiterals)
                return self.__main(deepcopy(cla), deepcopy(defLiterals))

    def __pickEquation(self, claus: list, ll: dict):
        for i in claus:
            if self.__checkClause(i, ll) != 1:
                return i
        return None

    def __flipBit(self, i: chr, ll: dict) -> None:
        if len(i) == 2:
            i = i[1:]
        ll[i] = 1 if ll[i] == 0 else 0

    def guideVarToTheTruth(self, var: chr, ll: dict):
        if len(var) == 1:
            ll[var] = 1

        elif len(var) == 2:
            ll[var[1:]] = 0

    def check(self, printt=1) -> None:
        if not self.unsat:
            solution = self.__main(deepcopy(self.clauses),
                                   deepcopy(self.literals))
            if solution:

                self.result = solution
                if printt:
                    print('sat')
                return

        if printt:
            print('unsat')

    def model(self) -> None:
        if self.result == None:
            self.check(0)

        if not self.unsat:
            self.__weKnow(self.result)

    def changeMode(self, x: int) -> bool:
        if 0 < x < 4:

            self.__mode = x
            return 1
        else:
            return 0


if __name__ == "__main__":
    SatLookAhead('input.txt').model()
