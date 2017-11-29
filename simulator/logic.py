
from typing import *
import random
import enum
from enum import Enum


# Please see https://namu.wiki/w/%ED%99%94%ED%88%AC/%ED%8C%A8
# Following cards are defined in the same order as appeared in the above link
# For the rules and terminologies: please see https://www.pagat.com/fishing/gostop.html

# card constants
class CardCode(Enum):
    JanBright=1
    JanRedRibbon=2
    Jan1=3
    Jan2=4

    FebBird=5
    FebRedRibbon=6
    Feb1=7
    Feb2=8

    MarBright=9
    MarRedRibbon=10
    Mar1=11
    Mar2=12

    AprBird=13
    AprRibbon=14
    Apr1=15
    Apr2=16

    MayBridge=17
    MayRibbon=18
    May1=19
    May2=20

    JunButterfly=21
    JunBlueRibbon=22
    Jun1=23
    Jun2=24

    JulPig=25
    JulRibbon=26
    Jul1=27
    Jul2=28

    AugBright=29
    AugBird=30
    Aug1=31
    Aug2=32

    SepFlask=33
    SepBlueRibbon=34
    Sep1=35
    Sep2=36

    OctDeer=37
    OctBlueRibbon=38
    Oct1=39
    Oct2=40

    NovBright=41
    NovDouble=42
    Nov1=43
    Nov2=44

    DecBright=45
    DecBird=46
    DecRibbon=47
    DecDoor=48


    JokerDouble1=49
    JokerDouble2=50
    JokerTriple=51


class Card(object):
    def __init__(self, code:CardCode):
        if not code in CardCode:
            raise Exception('Illegal code number')
        self._code = code

    @property
    def month(self) -> int:
        code = self._code.value
        if code >= 1 and code <= 48:
            return int((code - 1) / 4) + 1
        return None

    @property
    def is_bright(self) -> bool:
        return  self._code in [CardCode.JanBright, CardCode.MarBright, CardCode.AugBright, CardCode.NovBright, CardCode.DecBright]

    @property
    def is_subbright(self) -> bool:
        return self._code == CardCode.DecBright

    @property
    def is_bird(self) -> bool:
        return self._code in [CardCode.FebBird, CardCode.AprBird, CardCode.AugBird]

    @property
    def is_animal(self) -> bool:
        return self._code in [CardCode.FebBird, CardCode.AprBird, CardCode.MayBridge, CardCode.JunButterfly, CardCode.JulPig,
                              CardCode.AugBird, CardCode.SepFlask, CardCode.OctDeer, CardCode.DecBird]
    @property
    def is_red_ribbon(self) -> bool:
        return self._code in [CardCode.FebRedRibbon, CardCode.MarRedRibbon, CardCode.JanRedRibbon]

    @property
    def is_blue_ribbon(self) -> bool:
        return self._code in [CardCode.JunBlueRibbon, CardCode.SepBlueRibbon, CardCode.OctBlueRibbon]

    @property
    def is_plain_ribbon(self) -> bool:
        return self._code in [CardCode.AprRibbon, CardCode.MayRibbon, CardCode.JulRibbon, CardCode.DecRibbon]

    @property
    def is_ribbon(self) -> bool:
        return self._code in [CardCode.FebRedRibbon, CardCode.MarRedRibbon, CardCode.JanRedRibbon,
                              CardCode.JunBlueRibbon, CardCode.SepBlueRibbon, CardCode.OctBlueRibbon,
                              CardCode.AprRibbon, CardCode.MayRibbon, CardCode.JulRibbon, CardCode.DecRibbon]

    @property
    def pi_cnt(self) -> int:
        if self._code in [CardCode.Jan1, CardCode.Jan2, CardCode.Feb1, CardCode.Feb2, CardCode.Mar1, CardCode.Mar2,
                              CardCode.Apr1, CardCode.Apr2, CardCode.May1, CardCode.May2, CardCode.Jun1, CardCode.Jun2,
                              CardCode.Jul1, CardCode.Jul2, CardCode.Aug1, CardCode.Aug2, CardCode.Sep1, CardCode.Sep2,
                              CardCode.Oct1, CardCode.Oct2, CardCode.Nov1, CardCode.Nov2]:
            return 1

        if self._code in [CardCode.DecDoor, CardCode.NovDouble, CardCode.JokerDouble1, CardCode.JokerDouble2]:
            return 2

        if self._code == CardCode.JokerTriple: return 3
        return 0

    @property
    def is_bonus(self) -> bool:
        return self._code in [CardCode.JokerDouble1, CardCode.JokerDouble2, CardCode.JokerTriple]

    def __eq__(self, other:'Card'): return self._code.value == other._code.value
    def __gt__(self, other:'Card'): return self > other._code.value
    def __lt__(self, other:'Card'): return self < other._code.value
    def __hash__(self): return self._code.value
    def __str__(self):
        return '[' + self._code.name + ']'

CardSet = Set[Card]
def _cardset_to_str(cardset:CardSet):
    if len(cardset) == 0: return '-'
    res = ' '.join([str(c) for c in cardset])
    return res


class Player(object):
    def __init__(self):
        self._hand = set()
        self._acquired = set()
        self._shaked = set()
        self._go_cnt = 0
        self._shake_cnt = 0
        self._bomb_cnt = 0
        self._kukjin_as_doublepi = False
        self._latest_go_score = 0
        self._bomb_card_cnt = 0
        self._bbuck_cnt = 0
        self._consec_bbuck_cnt = 0
        self._president_cnt = 0

    def dump_str(self, indent=0):
        blank = ''
        if indent > 0: blank = ' ' * indent
        res  = blank + ("Go:{0}  Shake:{1}  Bomb:{2}  BBuck:{3}  BombCard:{4} Kukjin->TwoPi:{5}\n"
              .format(self._go_cnt, self._shake_cnt, self._bbuck_cnt, self._bbuck_cnt, self._bomb_card_cnt,
                      self._kukjin_as_doublepi))
        res += blank + 'Hand    : ' + _cardset_to_str(self._hand) + '\n'
        res += blank + 'Acquired: ' + _cardset_to_str(self._acquired) + '\n'
        res += blank + 'Shaked  : ' + _cardset_to_str(self._shaked) + '\n'
        return res

    def claim_president(self, month) -> bool:
        if month in self.president_months():
            self._president_cnt += 1
            return True
        return False

    def can_say_go(self) -> bool:
        cur_score = self.score(amplifier=False)
        return cur_score > self._latest_go_score and cur_score > 0

    def president_months(self) -> List[int]:
        cnt = dict()
        for c in self._hand: #type:Card
            m = c.month
            cnt[m] = cnt.get(m, 0) + 1

        res = []
        for k in cnt.keys():
            if cnt[k] == 4: res.append(m)
        return res

    def remove_pi(self) -> Union[Card, None]:
        pi = None
        pi_cnt = 0
        for c in self._acquired: #type: Card
            if pi_cnt == 0 or c.pi_cnt < pi_cnt:
                pi = c
                pi_cnt = c.pi_cnt
        if pi_cnt > 0: self._acquired.remove(pi)
        return pi

    def shakable_months(self) -> List[int]:
        cnt = dict()
        for c in self._hand: #type:Card
            m = c.month
            cnt[m] = cnt.get(m, 0) + 1

        res = []
        for k in cnt.keys():
            if cnt[k] == 3: res.append(m)
        return res

    def shake(self, c:Card) -> bool:
        m = c.month
        shakables = self.shakable_months()
        if m in shakables:
            for cc in self._hand: #type: Card
                if cc.month == m: self._shaked.insert(cc)
            return True
        return False

    def claim_go(self) -> bool:
        if not self.can_say_go(): return False
        self._latest_go_score = self.score(amplifier=False)
        self._go_cnt += 1
        return True

    def throw(self, c:Union[None, Card]) -> bool:
        if c._code is None:
            if self._bomb_card_cnt > 0:
                self._bomb_card_cnt -= 1
                return True
            return False
        else:
            if not c in self._hand: return False
            self._hand.remove(c)
            if c in self._shaked: self._shaked.remove(c)
            return True

    def acquire_bomb(self, bomb_cnt):
        self._bomb_card_cnt += bomb_cnt

    def score(self, amplifier = True) -> int:
        if self._president_cnt > 0: return 7
        bright_cnt = 0
        pi_cnt = 0
        subbright = False
        has_kukjin = False

        ribbon_cnt = 0
        red_ribbon_cnt = 0
        blue_ribbon_cnt = 0
        plain_ribbon_cnt = 0

        animal_cnt = 0
        bird_cnt = 0

        for c in self._acquired: #type: Card
            subbright        |= c.is_subbright
            has_kukjin       |= (c._code == CardCode.SepFlask)
            pi_cnt           += c.pi_cnt
            red_ribbon_cnt   += 1 if c.is_red_ribbon else 0
            blue_ribbon_cnt  += 1 if c.is_blue_ribbon else 0
            plain_ribbon_cnt += 1 if c.is_plain_ribbon else 0
            ribbon_cnt       += 1 if c.is_ribbon else 0
            animal_cnt       += 1 if c.is_animal else 0
            bird_cnt         += 1 if c.is_bird else 0
            bright_cnt       += 1 if c.is_bright else 0
            pi_cnt           += c.pi_cnt

        res = 0

        if self._kukjin_as_doublepi and has_kukjin:
            pi_cnt += 2
            animal_cnt -= 1

        if pi_cnt >= 10: res += pi_cnt - 9
        if animal_cnt >= 5 and animal_cnt <= 7: res += animal_cnt - 4
        elif animal_cnt > 7: res += 3
        if bird_cnt == 3: res += 5
        if ribbon_cnt >= 5: res += ribbon_cnt - 4

        if bright_cnt == 3 and subbright: res += 2
        elif bright_cnt == 3 and not subbright: res += 3
        elif bright_cnt == 4: res += 4
        elif bright_cnt == 5: res += 15

        if red_ribbon_cnt == 3: res += 3
        if blue_ribbon_cnt == 3: res += 3
        if plain_ribbon_cnt >= 3: res += 3

        if amplifier:
            if self._go_cnt == 1: res += 1
            elif self._go_cnt == 2: res += 2
            elif self._go_cnt > 0: res = res * (2 ** (self._go_cnt - 2))

            if animal_cnt >= 7: res *= 2 # mungbak

            if self._shake_cnt > 0: res = res * (2 ** self._shake_cnt)
            if self._bomb_cnt > 0: res = res * (2 ** self._bomb_cnt)

        return res

    @property
    def pibakable(self) -> bool:
        cnt = 0
        for c in list(self._acquired): #type: Card
            cnt += c.pi_cnt
        if cnt == 0 or cnt > 5: return False
        return True

    @property
    def gwangbakable(self) -> bool:
        cnt = 0
        for c in list(self._acquired): #type: Card
            cnt += 1 if c.is_bright else 0
        return cnt == 0

class GameState(Enum):
    Initialized = 0
    AskPresident = 1
    AnsweredPresident = 2
    AskCardToThrow = 3

    AnsweredCardToThrow = 4
    AskCardToCapture = 5
    AnsweredCardToCapture = 6


class Game(object):
    _round_cnt = 0
    _players = None
    _stock = None
    _board = None
    _state = None
    _round = None
    _turn = None
    _answer = None

    @property
    def num_player(self):
        return len(self._players)

    @property
    def goable_score(self):
        if self.num_player == 2: return 7
        elif self.num_player == 3: return 3

    def __init__(self, num_players:int=2):
        self._state = GameState.Initialized
        self._turn = 0
        self._answer = None

        if num_players == 2:
            num_hand = 10
            num_board = 8
        elif num_players == 3:
            num_hand = 7
            num_board = 6
        else: raise NotImplemented

        need_init = True
        self._round_cnt = 0

        while need_init:
            need_init = False
            self._players = list()
            self._stock = list()
            self._board = set()

            for _ in range(num_players):
                self._players.append(Player())

            for i in CardCode:
                self._stock.append(Card(i))

            # dealing cards
            random.shuffle(self._stock)
            for i in range(self.num_player):
                hand, self._stock = self._stock[:num_hand], self._stock[num_hand:]
                self._players[i]._hand.update(hand)

            board, self._stock = self._stock[:num_board], self._stock[num_board:]
            self._board.update(board)

            # the 1st player get the bonus cards on the board 
            for c in self._board: #type: Card
                if c.is_bonus: self._players[0]._acquired.add(c)
            self._board = set([c for c in self._board if not c.is_bonus])


            # if 'president' occured on the board, we re-initialize the whole game.
            cnt = dict()
            for c in self._board: #type:Card
                m = c.month
                cnt[m] = cnt.get(m, 0) + 1

            res = []
            for k in cnt.keys():
                if cnt[k] == 4:
                    need_init = True

        self.i_deal()
        return

    def _deal(self):
        if self._state in [GameState.Initialized, GameState.AnsweredPresident]:
            while self._turn < len(self._players):
                months = self._players[self._turn].president_months()
                if len(months) > 0: return
                self._turn += 1

            self._turn = 0
            self._state = GameState.AskCardToThrow
            return
        elif self._state == GameState.AnsweredCardToThrow:
            if self._answer is None: return


    def action_reqfields(self):
        if self._state == GameState.AskPresident:
            return ['card']
        elif self._state == GameState.AskCardToThrow:
            return ['card', 'shake_or_bomb']


    
    def action(self, ans:dict) -> bool:
        required = self.answer_reqfields()
        for key in required:
            if not key in ans: return False
        self._answer = ans

        if self._state == GameState.AskPresident:
            self._state = GameState.AnsweredPresident

        self._deal()
        return True


    @property
    def state(self):
        return self._state

    @property
    def turn(self):
        return self._turn

    @property
    def turn_as_player(self):
        return self._players[self._turn]


    def dump_str(self, indent:int=4):
        res  = 'Round #{0}\n'.format(self._round_cnt)
        res += 'Board: {0}\n'.format(_cardset_to_str(self._board))
        res += 'Stock: {0}\n'.format(_cardset_to_str(self._stock))
        for pidx, p in enumerate(self._players):
            res += 'Player #{0} ====\n'.format(pidx)
            res += p.dump_str(indent=indent)

        return res


class TestConsole(object):
    def __init__(self, num_players=2):
        self._game = Game(num_players)

console = TestConsole(2)

