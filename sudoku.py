# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, print_function, division)

from copy import deepcopy
from itertools import combinations

class Cell:

    def __init__(self):
        self.value = 0
        self.row = set()
        self.col = set()
        self.sq = set()
        self.rm_values = set()

    def isSet(self):
        return self.value > 0

    @property
    def values(self):
        if self.value:
            return set()
        else:
            return set(range(1, 10)) - self.row - self.col - self.sq - self.rm_values

    def set(self, val):
        if val > 0:
            if val not in self.row and val not in self.col and val not in self.sq:
                self.value = val
                self.row.add(val)
                self.col.add(val)
                self.sq.add(val)
            else:
                raise ValueError

    def rm_value(self, val):
        if isinstance(val, int):
            self.rm_values.add(val)
        elif isinstance(val, set):
            self.rm_values |= val

    def __repr__(self):
        if self.value == 0:
            return ' '
        else:
            return repr(self.value)


def carre(i,j):
    return i//3+3*(j//3)

def are_neigh(i,j,k,l):
    return (i==k) + (j==l) + (carre(i,j)==carre(k,l))

def coord(dim, i, k):
    if dim==0:
        return i, k
    elif dim==1:
        return k, i
    elif dim==2:
        return 3*(i%3)+k%3,3*(i//3)+k//3


class Sudoku:

    def __init__(self, start=None): #(((0,)*9, )*9):
        self.grid = { }
        self.turns = 0

        # Cells initialisation
        for i in range(9):
            # self.grid[i] = { }
            for j in range(9):
                self.grid[i,j] = Cell()

        # Rows initialisation
        for j in range(9):
            row = set()
            for i in range(9):
                self.grid[i,j].row = row
        # Columns initialisation
        for i in range(9):
            col = set()
            for j in range(9):
                self.grid[i,j].col = col
        # Squares initialisation
        for c in range(9):
            sq = set()
            for i in range(3):
                for j in range(3):
                    self.grid[i+3*(c%3),j+3*(c//3)].sq = sq

        if start:
            for j, c in enumerate(start):
                for i, v in enumerate(c):
                    try:
                        self.set(i, j, v)
                    except:
                        print('###', i, j, v)
                        raise

    def __repr__(self):
        result = '-'*25 + "\n"
        for j in range(8, -1, -1):
            line = ''
            for i in range(0, 9, 3):
                line += "| %r %r %r " % (tuple( self.grid[k,j] for k in range(i, i+3) ))
            result += "%s|\n" % line
            if not j%3:
                result += '-'*25 + "\n"
        return result.rstrip()

    @property
    def solved(self):
        return all( [ self.grid[i,j].isSet() for i in range(9) for j in range(9) ] )

    def set(self, i, j, val):
        self.grid[i,j].set(val)

    def rm_value(self, i, j, val):
        self.grid[i,j].rm_value(val)

    def neigh_values(self, x, y):
        row_result = set()
        for i in range(9):
            if i != x:
                row_result |= self.grid[i,y].values
        col_result = set()
        for j in range(9):
            if j != y:
                col_result |= self.grid[x,j].values
        sq_result = set()
        for i in range(3):
            for j in range(3):
                if i != x%3 or j != y%3:
                    sq_result |= self.grid[i+3*(x//3),j+3*(y//3)].values
        return (row_result, col_result, sq_result)

    def rech_solitaire_nu(self):
        chgt = False
        # Solitaire nu
        for i in range(9):
            for j in range(9):
                l = self.grid[i,j].values
                if len(l) == 1:
                    v = l.pop()
                    print("%d,%d -> %d |" % (i, j, v), end=' ')
                    self.set(i, j, v)
                    chgt = True
                    self.turns += 1

        return chgt

    def rech_solitaire_camoufle(self):
        chgt = False
        # Solitaire camouflé
        for i in range(9):
            for j in range(9):
                l = self.grid[i,j].values
                for a in ( l - x for x in self.neigh_values(i, j) ):
                    if len(a) == 1:
                        v = a.pop()
                        print("%d,%d => %d |" % (i, j, v), end=' ')
                        self.set(i, j, v)
                        chgt = True
                        self.turns += 1
                        break

        return chgt

    def rech_gpes_dominants(self):
        chgt = False
        for v in range(1, 10):
            candidates = [ (i,j) for i in range(9) for j in range(9) if v in self.grid[i,j].values ]
            for candidat in candidates:
                for k in (0, 1):
                    copains = [ a for a in candidates if a[k]==candidat[k] and are_neigh(*candidat,*a) >= 2 ]
                    candid_mince = [ a for a in candidates if a[k]==candidat[k] and a not in copains ]
                    candid_sq = [ a for a in candidates if carre(*a)==carre(*candidat) and a not in copains ]
                    if not candid_mince:
                        for cell in candid_sq:
                            print("%d,%d -> -%d |" % (*cell, v), end=' ')
                            self.rm_value(*cell, v)
                            chgt = True
                            self.turns += 1
                    elif not candid_sq:
                        for cell in candid_mince:
                            print("%d,%d -> -%d |" % (*cell, v), end=' ')
                            self.rm_value(*cell, v)
                            chgt = True
                            self.turns += 1

        return chgt

    def rech_gpes_nus(self):
        chgt = False
        candidates = [ (i,j,self.grid[i,j].values) for i in range(9) for j in range(9) if self.grid[i,j].values ]
        for (i,j,v) in candidates:
            current_gpe = [(i,j)]
            for (k,l,m) in candidates:
                if all([ 1 <= are_neigh(*g,k,l) <= 2 for g in current_gpe ]) and m <= v:
                    current_gpe.append((k,l))
            if len(current_gpe) == len(v):
                for (k,l,m) in candidates:
                    intersect = m&v
                    if all([ 1 <= are_neigh(*g,k,l) <= 2 for g in current_gpe ]) and intersect:
                        print("%d,%d => -%s |" % (k,l,intersect), end=' ')
                        self.rm_value(k,l,intersect)
                        chgt = True
                        self.turns += 1

        return chgt

    def rech_gpes_camoufles(self):
        chgt = False

        candidates = [ (i,j,self.grid[i,j].values) for i in range(9) for j in range(9) ]
        values_count = ( # col, lig, sq
            { i: {j: set() for j in range(1, 10)} for i in range(9)},
            { i: {j: set() for j in range(1, 10)} for i in range(9)},
            { i: {j: set() for j in range(1, 10)} for i in range(9)},
        )
        for (i, j, values) in candidates:
            for v in values:
                values_count[0][i][v].add((i,j))
                values_count[1][j][v].add((i,j))
                values_count[2][carre(i,j)][v].add((i,j))

        for dim in (0, 1, 2):
            for k in range(9):
                count_values =  [ {'vals': set((v, )), 'cells': c} for (v,c) in values_count[dim][k].items() if len(c) > 1 ]
                # len(c) = 0 correspond aux valeurs fixées. Et 1 au solitaire nu...

                all_combinations = []
                for n in range(1,5): # On limite au quatuor (suffisant d'après la doc)
                    all_combinations += combinations(count_values, n)
                all_count_values = []
                for glop in all_combinations:
                    tmp = {'vals': set(), 'cells': set() }
                    for plop in glop:
                        tmp['vals'] |= plop['vals']
                        tmp['cells'] |= plop['cells']
                    all_count_values.append(tmp)

                for result in all_count_values:
                    if result['vals'] and len(result['cells'])==len(result['vals']):
                        for cell in result['cells']:
                            diff = self.grid[cell].values - result['vals']
                            if diff:
                                print("%d,%d ~> -%s |" % (*cell, diff), end=' ')
                                self.rm_value(*cell, diff)
                                chgt = True
                                self.turns += 1

        return chgt

    def solve(self):
        # https://fr.wikibooks.org/wiki/Résolution_de_casse-têtes/Résolution_du_sudoku
        chgt = (True, )
        while not self.solved and any(chgt):
            chgt = (
                self.rech_solitaire_nu(),
                self.rech_solitaire_camoufle(),
            )
            if not any(chgt):
                chgt = (
                    self.rech_gpes_dominants(),
                    self.rech_gpes_nus(),
                    self.rech_gpes_camoufles(),
                )

            #print("\n%r" % self)
            #raw_input("Press Enter to continue...")
        print("\n%r\n###### Résolu: %s en %d coups #######" % (self, self.solved, self.turns))
        # if not self.solved:
        #     print([ (i,j,self.grid[i,j].values) for i in range(9) for j in range(9) ])


# s = Sudoku()
# s.set(0,0,5); s.set(1,0,7); s.set(4,0,1)
# s.set(0,1,9); s.set(3,1,4); s.set(6,1,1); s.set(7,1,2); s.set(8,1,7)
# s.set(1,2,2); s.set(3,2,8); s.set(5,2,9); s.set(7,2,4)
# s.set(0,3,2); s.set(4,3,8); s.set(8,3,3)
# s.set(0,4,8); s.set(1,4,3); s.set(5,4,6); s.set(6,4,2)
# s.set(0,5,6); s.set(1,5,1); s.set(5,5,7); s.set(6,5,4); s.set(7,5,8)
# s.set(6,6,7); s.set(7,6,5); s.set(8,6,4)
# s.set(0,7,4); s.set(1,7,8); s.set(2,7,6); s.set(5,7,5)
# s.set(1,8,5); s.set(3,8,2); s.set(4,8,3); s.set(6,8,6); s.set(7,8,9)
# print("%r" % s)
# s.solve()

# s = Sudoku()
# s.set(3,0,2); s.set(4,0,3); s.set(5,0,8)
# s.set(2,1,4)
# s.set(2,2,2); s.set(5,2,7); s.set(6,2,3); s.set(7,2,5)
# s.set(0,3,1); s.set(2,3,5); s.set(4,3,4); s.set(8,3,3)
# s.set(0,4,4); s.set(3,4,8); s.set(5,4,3); s.set(8,4,7)
# s.set(0,5,7); s.set(4,5,9); s.set(6,5,6); s.set(8,5,4)
# s.set(1,6,5); s.set(2,6,3); s.set(3,6,9); s.set(6,6,2)
# s.set(6,7,8)
# s.set(3,8,3); s.set(4,8,2); s.set(5,8,5)
# print("%r" % s)
# s.solve()

# s = Sudoku((
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
#     (0,0,0,0,0,0,0,0,0),
# ))


s = Sudoku((
       (0,6,0,8,0,0,0,0,1),
       (0,0,0,0,0,0,0,9,3),
       (3,0,0,9,0,0,0,0,0),
       (0,0,2,0,0,0,0,0,0),
       (8,5,1,0,7,0,4,3,2),
       (0,0,0,0,0,0,9,0,0),
       (0,0,0,0,0,3,0,0,8),
       (2,4,0,5,0,0,0,0,0),
       (1,0,0,0,0,4,0,7,0),
))
print("%r" % s)
s.solve()
# if not s.solved:
#     candidates = ([ (i,j,s.grid[i,j].values) for i in range(9) for j in range(9) ])
#     for (i,j,vals) in candidates:
#         for v in vals:
#             option = deepcopy(s)
#             option.set(i,j,v)
#             option.solve()

# s = Sudoku((
#         (0,3,0,0,0,0,0,0,7),
#         (0,0,2,0,0,0,0,0,0),
#         (8,9,0,4,0,7,0,1,0),
#         (3,7,0,0,9,5,0,0,4),
#         (0,0,9,0,8,0,1,0,0),
#         (1,0,0,7,4,0,0,8,9),
#         (0,1,0,6,0,4,0,3,8),
#         (0,0,0,0,0,0,5,0,0),
#         (2,0,0,0,0,0,0,4,0),
# ))
# print("%r" % s)
# s.solve()

# s = Sudoku((
#        (6,2,0,0,5,0,0,0,0),
#        (8,0,7,0,0,0,0,5,6),
#        (0,5,9,0,0,8,0,0,0),
#        (0,0,0,4,0,2,0,7,0),
#        (0,0,1,0,0,0,6,0,0),
#        (0,8,0,7,0,1,0,0,0),
#        (0,0,0,9,0,0,7,6,0),
#        (5,4,0,0,0,0,8,0,0),
#        (0,0,0,0,2,0,0,4,3),
# ))
# print("%r" % s)
# s.solve()

# s = Sudoku((
#        (0,3,6,5,0,7,0,0,0),
#        (0,0,2,0,9,0,0,0,0),
#        (5,0,4,0,0,0,0,0,0),
#        (6,0,7,0,0,3,0,1,0),
#        (0,0,0,2,1,9,0,0,0),
#        (0,1,9,7,0,6,3,0,8),
#        (0,6,5,0,0,0,1,0,7),
#        (0,0,0,0,6,0,5,0,0),
#        (0,0,1,9,7,5,6,4,0),
# ))
# print("%r" % s)
# s.solve()

# s = Sudoku((
#     (5,7,0,3,0,4,1,8,0),
#     (4,3,2,0,0,0,5,9,7),
#     (1,8,0,5,0,7,0,3,0),
#     (0,6,4,0,0,0,7,5,0),
#     (9,1,0,0,0,5,0,0,3),
#     (0,2,5,0,0,0,9,6,0),
#     (0,9,0,4,8,6,0,1,5),
#     (0,5,1,0,0,0,8,0,0),
#     (0,4,0,1,5,2,0,7,9),
# ))
# print("%r" % s)
# s.solve()

# s = Sudoku((
#     (0,1,6,0,0,0,0,0,0),
#     (7,0,0,0,0,0,2,6,0),
#     (8,0,2,0,6,0,0,0,9),
#     (5,7,1,3,8,2,6,9,4),
#     (2,6,3,1,4,9,0,5,0),
#     (9,8,4,6,0,0,3,2,1),
#     (1,0,0,7,3,6,5,0,2),
#     (6,2,7,0,0,0,0,0,3),
#     (0,0,0,0,0,0,9,7,6),
# ))
# print("%r" % s)
# # s.rech_gpes_camoufles(); print()
# s.solve()

s = Sudoku((
    (5,7,0,0,0,0,0,0,9),
    (0,0,0,5,6,0,0,0,0),
    (0,6,0,0,0,0,3,0,5),
    (0,5,8,4,1,0,0,0,0),
    (9,4,0,0,2,0,5,0,1),
    (0,0,2,9,5,0,8,0,4),
    (4,2,1,0,3,0,0,5,0),
    (0,0,0,1,0,5,2,0,0),
    (0,0,5,0,7,0,0,1,6),
))
print("%r" % s)
# s.rech_gpes_nus() ; print()
# s.rech_gpes_camoufles() ; print()
# s.rech_gpes_camoufles() ; print()
s.solve()
# if not s.solved:
#     candidates = ([ (i,j,s.grid[i,j].values) for i in range(9) for j in range(9) ])
#     for (i,j,vals) in candidates:
#         for v in vals:
#             option = deepcopy(s)
#             option.set(i,j,v)
#             option.solve()

# s = Sudoku((
#     (0,3,0,0,0,0,0,0,7),
#     (0,0,2,0,0,0,0,0,0),
#     (8,9,0,4,0,7,0,1,0),
#     (3,7,0,0,9,5,0,0,4),
#     (0,0,9,0,8,0,1,0,0),
#     (1,0,0,7,4,0,0,8,9),
#     (0,1,0,6,0,4,0,3,8),
#     (0,0,0,0,0,0,5,0,0),
#     (2,0,0,0,0,0,0,4,0),
# ))
# print("%r" % s)
# s.solve()

# conv = dict(zip('abcdefghj', range(9))); conv.update(zip('ABCDEFGHJ', range(8,-1,-1)))
# for a in conv:
#     sol =  sol.replace(a, str(conv[a]))
# print(sol)
