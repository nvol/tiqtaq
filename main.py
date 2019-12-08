import unittest
from itertools import permutations as pmt
from sys import argv
import json
from time import time as now

OPERATORS = ('e', 'a', 'b', 'c', 'd', 'da', 'db', 'dc')
WIN_SETS = (
        (1,2,3),(8,0,4),(7,6,5),
        (1,8,7),(2,0,6),(3,4,5),
        (1,0,5),(3,0,7),
)
KEY_SET = {'q':1,'w':2,'e':3,'d':4,'c':5,'x':6,'z':7,'a':8,'s':0}

def filter(d, v):
    cnt = 0
    for k in d:
        if d[k] == v:
            cnt += 1
    return cnt, '%.2f%%' % (100.*cnt/len(d))

def inv(op):
    if len(op) == 2 and 'd' in op:
        return op
    return ''.join(
      [{'a':'c','c':'a'}.get(k) or k for k in op]
    )

def transform(turns, op):
    return_int = False
    if type(turns) is int:
        turns = [turns]
        return_int = True
    for t in op:
        if t == 'd':
            turns = [(10-i-1)%8+1 if i!=0 else 0 for i in turns]
        elif t in 'abc':
            inc = (ord(t)-ord('a')+1)*2
            turns = [(i+inc-1)%8+1 if i!=0 else 0 for i in turns]
    if return_int:
        turns = turns[0]
    return turns

class Field:
    def __init__(self, turns=None):
        self.op = None # operator to transform turns->normal
        self.turns = list()
        self._result = None
        if turns:
            for i in turns:
                ret = self.add_turn(i, without_normalization=True)
            self.normalize()

    @property
    def normal(self):
        if self.op is None:
            self.normalize()
        return transform(self.turns, self.op)

    def history(self): # returns str history if game is over else None
        if self.is_game_finished():
            return ''.join([str(i) for i in self.normal])

    def add_turn(self, pos, without_normalization=None): # returns True if accepted
        if not self.is_game_finished():
            if pos not in self.turns:
                self.turns.append(pos)
                if not without_normalization:
                    self.normalize()
                return True
        return False

    def XO(self, pos, is_normalized):
        turns = self.turns
        if is_normalized:
            turns = transform(turns, self.op)
        ret = ' '
        if pos in turns:
            seq = turns.index(pos)
            ret = 'O' if seq%2 else 'X'
        return ret

    def normalize(self):
        normalized_turns = None
        for op in OPERATORS:
            turns = transform(self.turns, op)
            if normalized_turns is None or turns < normalized_turns:
                normalized_turns = turns
                self.op = op
        return normalized_turns, op

    def show(self, is_normalized=None):
        n = bool(is_normalized)
        print('='*7)
        print('|%s %s %s|' % (self.XO(1,n), self.XO(2,n), self.XO(3,n)))
        print('|%s %s %s|' % (self.XO(8,n), self.XO(0,n), self.XO(4,n)))
        print('|%s %s %s|' % (self.XO(7,n), self.XO(6,n), self.XO(5,n)))
        print('='*7)
        print()

    def Xwins(self): # returns win_set if X wins and None otherwise
        Xposes = self.turns[0::2]
        for w in WIN_SETS:
            if w[0] in Xposes and w[1] in Xposes and w[2] in Xposes:
                return w
        return None

    def Owins(self): # returns win_set if O wins and None otherwise
        Oposes = self.turns[1::2]
        for w in WIN_SETS:
            if w[0] in Oposes and w[1] in Oposes and w[2] in Oposes:
                return w
        return None

    def draw(self):
        return len(self.turns) == 9

    def is_game_finished(self):
        if self._result is not None:
            return True
        x = self.Xwins()
        o = self.Owins()
        if x or o or self.draw():
            self._result = bool(x) - bool(o)
            return True
        return False

    def who_wins(self): # returns 1 if X wins, -1 if O wins, 0 if draw
        if self.is_game_finished():
            return self._result

    def accept_turn(self):
        while(True):
            key = input().lower().strip()
            if key in KEY_SET:
                accepted = self.add_turn(KEY_SET[key])
                if accepted:
                    break


class Test(unittest.TestCase):
    def test_inv(self):
        self.assertEqual(inv('b'), 'b')
        self.assertEqual(inv('da'), 'da')
        self.assertEqual(inv('ad'), 'ad')
        self.assertEqual(inv('d'), 'd')
        self.assertEqual(inv('c'), 'a')
        self.assertEqual(inv('e'), 'e')
        self.assertEqual(inv(''), '')
        self.assertEqual(inv('db'), 'db')
        self.assertEqual(inv('bd'), 'bd')
        self.assertEqual(inv('a'), 'c')
        self.assertEqual(inv('dc'), 'dc')
        self.assertEqual(inv('cd'), 'cd')

    def test_transform(self):
        self.assertEqual(transform([3,5],'dc'), [5,3])
        self.assertEqual(transform([1,7,0],'dc'), [7,1,0])
        self.assertEqual(transform([2,3],'d'), [8,7])
        self.assertEqual(transform([1,6,4],'e'), [1,6,4])
        self.assertEqual(transform([4,3,8],''), [4,3,8])
        self.assertEqual(transform([0,5],'a'), [0,7])
        self.assertEqual(transform([0,5],'c'), [0,3])
        self.assertEqual(transform([1,2,3,4,5],'b'), [5,6,7,8,1])
        self.assertEqual(transform([1,2,3,4,5],'db'), [5,4,3,2,1])

    def test_transform_and_inv(self):
        for op in OPERATORS:
            #t = [1,3,2,4,5,7,6,0,8]
            t = [1,3]
            print(t, op, transform(t, op), inv(op))
            self.assertEqual(transform(transform(t, op), inv(op)), t)

    def test_normalize(self):
        f = Field((3,5))
        self.assertEqual(f.normal, [1,3])
        self.assertEqual(f.op, 'c')
        f = Field((7,3,6))
        self.assertEqual(f.normal, [1,5,2])
        self.assertEqual(f.op, 'dc')
        f = Field((1,8,5,0))
        self.assertEqual(f.normal, [1,2,5,0])
        self.assertEqual(f.op, 'd')
        f = Field((0,))
        self.assertEqual(f.normal, [0])
        self.assertEqual(f.op, 'e')
        f = Field((1,0,5))
        self.assertEqual(f.normal, [1,0,5])
        self.assertEqual(f.op, 'e')
        f = Field((5,0,1))
        self.assertEqual(f.normal, [1,0,5])
        self.assertEqual(f.op, 'b')

if __name__ == '__main__':
    # unittest.main()

    if len(argv) > 1:
        if argv[1] == 'game':
            print('Use qweasdzxc and Enter keys to make a turn')
            field = Field()
            while(not field.is_game_finished()):
                field.accept_turn()
                field.show()
            print('O wins' if field.Owins()
              else 'X wins' if field.Xwins() else 'draw')
        elif argv[1] == 'stat':
            start = now()
            cntr, next_limit = 0, 0
            stats = dict()
            total_combinations = 120960 # 3 * 8!
            for first_turn in range(3): # 0,1,2 only (normalized turn)
                for other_turns in pmt({0,1,2,3,4,5,6,7,8} - {first_turn}):
                    cntr += 1
                    turns = (first_turn,) + other_turns
                    game = Field(turns)
                    h, w = game.history(), game.who_wins()
                    stats[h] = w
                    if cntr >= next_limit:
                        print('.', end='', flush=True)
                        next_limit += total_combinations // 10 - 1
                    #if cntr >= 100: break #@@@
            print()
            with open('tiqtaq.json', 'w') as f:
                json.dump(stats, f, indent=2, sort_keys=True)
            print('elapsed %.3f seconds' % (now() - start))
            print('dict len:', len(stats))
            print('   X won:', filter(stats, 1))
            print('   O won:', filter(stats, -1))
            print('    draw:', filter(stats, 0))
    else:
        print('please run with param `game` or `stat`')
