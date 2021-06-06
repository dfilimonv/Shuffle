import itertools
import copy

class Monomial:
    def __init__(self, partition):
        self.partition = sorted(partition, key = lambda x: (len(x), x[0]))
        #self.partition = tuple(tuple(l) for l in partition)
        self.degree = len(partition)
        self.arity = sum(len(l) for l in partition)
        self.divisors_set = False

    def __repr__(self):
        return(str(self.partition))

    def __eq__(self,other):
        return self.partition == other.partition

    def __hash__(self):
        return hash(self.part_to_tuple(self.partition))

    def __gt__(self,other):
        if self.arity > other.arity:
            return True
        if self.arity < other.arity:
            return False
        for i in range(len(self.partition)):
            if len(self.partition[i]) > len(other.partition[i]):
                return True
            if len(self.partition[i]) < len(other.partition[i]):
                return False
            for j in range(len(self.partition[i])):
                if self.partition[i][j] > other.partition[i][j]:
                    return True
                if self.partition[i][j] < other.partition[i][j]:
                    return False
        return True
    
    @staticmethod
    def normalized_part(part):
        parts = copy.deepcopy(part)
        keys = sorted(list(itertools.chain.from_iterable(parts)))
        vals = range(len(keys))
        d = dict(zip(keys,vals))
        for p in parts:
            for i in range(len(p)):
                p[i] = d[p[i]]
        return parts

    @staticmethod
    def list_compliment(l,n):
        compliment = set(range(n))
        for s in l:
            compliment.remove(s)
        return sorted(list(compliment))

    @staticmethod
    def part_mul(part, p1, p2):
        def part_list(p, l):
            res = copy.deepcopy(p)
            for i in range(len(p)):
                for j in range(len(p[i])):
                    res[i][j] = l[p[i][j]]
            return res
        res = part_list(p1, part[0]) + part_list(p2, part[1])
        res.sort(key = lambda x:(len(x), x[0]))
        return res

    @staticmethod
    def part_to_tuple(part):
        return tuple(tuple(l) for l in part)

    @staticmethod
    def powerset(l):
        return itertools.chain.from_iterable(
                itertools.combinations(l,i) for i in range(1, len(l)+1)
                )

    @staticmethod
    def sublist_gen(l, r):
        n = len(l)
        indices = list(range(r))
        yield [l[i] for i in indices]
        while True:
            for i in reversed(range(r)):
                if indices[i] != i + n - r:
                    break
            else:
                return
            indices[i] += 1
            for j in range(i+1, r):
                indices[j] = indices[j-1] + 1
            yield [l[i] for i in indices]

    def mul(self, partition, other):
        def part_list(p, l):
            res = copy.deepcopy(p)
            for i in range(len(p)):
                for j in range(len(p[i])):
                    res[i][j] = l[p[i][j]]
            return res
        return Monomial(part_list(self.partition, partition[0]) +
                        part_list(other.partition, partition[1]))

    def div_part(self, part):
        print(self)
        print(part)
        partition = copy.deepcopy(self.partition)
        new_part = [p for p in partition if p not in part]
        keys = sorted(list(itertools.chain.from_iterable(new_part)))
        vals = range(self.arity - sum(len(l) for l in part))
        d = dict(zip(keys, vals))
        for p in new_part:
            for i in range(len(p)):
                p[i] = d[p[i]]
        return new_part

    def divisors(self):
        if not self.divisors_set:
            self.set_divisors()
        return self.divisors

    def set_divisors(self):
        if self.divisors_set:
            return
        self.divisors = dict()
        self.divisors_set = True
        for t in self.powerset(self.partition):
            t = [list(s) for s in t]
            m = Monomial(self.normalized_part(t))
            self.divisors[m] = self.divisors.get(m, []) + [t]

    def is_divisible(self, other):
        if other in self.divisors():
            return True
        return False

    def insertions(self,other):
        if not self.is_divisible(other):
            yield None
        for p in self.divisors[self.part_to_tuple(other.partition)]:
            p1 = sorted(list(itertools.chain.from_iterable(p)))
            p2 = self.list_compliment(p1, self.arity)
            m2 = self.normalized_part([l for l in self.partition if l not in p])
            def insertion(m):
                m1 = m.partition 
                print(p1,p2,m1,m2)
                return Monomial(self.part_mul([p1,p2], m1, m2))
            yield insertion

    def overlaps(self,other):
        self.set_divisors()
        other.set_divisors()
        divs_1 = set(self.divisors.keys())
        divs_2 = set(other.divisors.keys())
        common_divs = set.intersection(divs_1, divs_2)
        res = set()
        print(common_divs)
        for div in common_divs:
            n1 = other.arity - div.arity 
            n = self.arity + n1
            l = list(range(n))
            checked = set()
            print(other.divisors[div])
            for ins in other.divisors[div]:
                print(ins)
                m1 = Monomial(self.normalized_part(other.div_part(ins)))
                if m1 in checked:
                    continue
                for p1 in self.sublist_gen(l, n1):
                    p2 = self.list_compliment(p1,n)
                    m = m1.mul([p1,p2], self)
                    if m.is_divisible(other):
                        res.add(m)
                checked.add(m1)
        return res




