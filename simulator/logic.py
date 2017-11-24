
from typing import *
from enum import Enum
import random

# Please see https://namu.wiki/w/%ED%99%94%ED%88%AC/%ED%8C%A8
# Following cards are defined in the same order as appeared in the above link

# card constants
class CardCode(Enum):
    JanLight=1
    JanRedFlag=2
    Jan1=3
    Jan2=4

    FebBird=5
    FebRedFlag=6
    Feb1=7
    Feb2=8

    MarLight=9
    MarRedFlag=10
    Mar1=11
    Mar2=12

    AprBird=13
    AprFlag=14
    Apr1=15
    Apr2=16

    MayBridge=17
    MayFlag=18
    May1=19
    May2=20

    JunButterfly=21
    JunBlueFlag=22
    Jun1=23
    Jun2=24

    JulPig=25
    JulFlag=26
    Jul1=27
    Jul2=28

    AugLight=29
    AugBird=30
    Aug1=31
    Aug2=32

    SepFlask=33
    SepBlueFlag=34
    Sep1=35
    Sep2=36

    OctDeer=37
    OctBlueFlag=38
    Oct1=39
    Oct2=40

    NovLight=41
    NovDouble=42
    Nov1=43
    Nov2=44

    DecLight=45
    DecBird=46
    DecFlag=47
    DecDoor=48


    JokerDouble1=49
    JokerDouble2=50
    JokerTriple=51
    Bomb=52

class Card(object):
    def __init__(self, code):
        if code < 1 or code > 52:
            raise Exception('Illegal code number')
        self._code = code

    @property
    def month(self) -> int:
        if self._code >= 1 and self._code <= 48:
            return int((self._code - 1) / 4) + 1
        return -1

    @property
    def is_light(self) -> bool:
        return  self._code in [Card.JanLight, Card.MarLight, Card.AugLight, Card.NovLight, Card.DecLight]

    @property
    def is_sublight(self) -> bool:
        return self._code == Card.DecLight

    @property
    def is_bird(self) -> bool:
        return self._code in [Card.FebBird, Card.AprBird, Card.AugBird]

    @property
    def is_animal(self) -> bool:
        return self._code in [Card.FebBird, Card.AprBird, Card.MayBridge, Card.JunButterfly, Card.JulPig,
                              Card.AugBird, Card.SepFlask, Card.OctDeer, Card.DecBird]
    @property
    def is_red_flag(self) -> bool:
        return self._code in [Card.FebRedFlag, Card.MarRedFlag, Card.JanRedFlag]

    @property
    def is_blue_flag(self) -> bool:
        return self._code in [Card.JunBlueFlag, Card.SepBlueFlag, Card.OctBlueFlag]

    @property
    def is_plane_flag(self) -> bool:
        return self._code in [Card.AprFlag, Card.MayFlag, Card.JulFlag, Card.DecFlag]

    @property
    def is_flag(self) -> bool:
        return self._code in [Card.FebRedFlag, Card.MarRedFlag, Card.JanRedFlag,
                              Card.JunBlueFlag, Card.SepBlueFlag, Card.OctBlueFlag,
                              Card.AprFlag, Card.MayFlag, Card.JulFlag, Card.DecFlag]

    @property
    def pi_cnt(self) -> int:
        if self._code in [Card.Jan1, Card.Jan2, Card.Feb1, Card.Feb2, Card.Mar1, Card.Mar2,
                              Card.Apr1, Card.Apr2, Card.May1, Card.May2, Card.Jun1, Card.Jun2,
                              Card.Jul1, Card.Jul2, Card.Aug1, Card.Aug2, Card.Sep1, Card.Sep2,
                              Card.Oct1, Card.Oct2, Card.Nov1, Card.Nov2]:
            return 1

        if self._code in [Card.DecDoor, Card.NovDouble, Card.JokerDouble1, Card.JokerDouble2]:
            return 2

        if self._code == Card.JokerTriple: return 3
        return 0

    @property
    def is_bonus(self) -> bool:
        return self._code in [Card.JokerDouble1, Card.JokerDouble2, Card.JokerTriple]

    def __eq__(self, other:'Card'): return self.value == other.value
    def __gt__(self, other:'Card'): return self > other._code
    def __lt__(self, other:'Card'): return self < other._code
    def __hash__(self): return self._code

CardSet = Set[Card]



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

    def dump(self):
        print("Go:{0}  Shake:{1}  Bomb:{2}  BBuck:{3}  BombCard:{4}"
              .format(self._go_cnt, self._shake_cnt, self._bbuck_cnt, self._bbuck_cnt, self._bomb_card_cnt))
        print("Hand: [" + "" + "]")

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

    def throw(self, c:Card) -> bool:
        if c._code == c.Bomb:
            if self._bomb_card_cnt > 0:
                self._bomb_card_cnt -= 1
                return True
            if self._bomb_card_cnt == 0:
                if Card(Card.Bomb) in self._hand:
                    self._hand.remove(Card(Card.Bomb))
            return False
        else:
            if not c in self._hand: return False
            self._hand.remove(c)
            if c in self._shaked: self._shaked.remove(c)
            return True

    def acquire_bomb(self, bomb_cnt):
        self._bomb_card_cnt = bomb_cnt
        self._hand.add(Card(Card.Bomb))

    def score(self, amplifier = True) -> int:
        if self._president_cnt > 0: return 7
        light_cnt = 0
        pi_cnt = 0
        sublight = False
        has_kukjin = False

        flag_cnt = 0
        red_flag_cnt = 0
        blue_flag_cnt = 0
        plane_flag_cnt = 0

        animal_cnt = 0
        bird_cnt = 0

        for c in self._acquired: #type: Card
            sublight       |= c.is_sublight
            has_kukjin     |= (c._code == Card.SepFlask)
            pi_cnt         += c.pi_cnt
            red_flag_cnt   += 1 if c.is_red_flag else 0
            blue_flag_cnt  += 1 if c.is_blue_flag else 0
            plane_flag_cnt += 1 if c.is_plane_flag else 0
            flag_cnt       += 1 if c.is_flag else 0
            animal_cnt     += 1 if c.is_animal else 0
            bird_cnt       += 1 if c.is_bird else 0
            light_cnt      += 1 if c.is_light else 0
            pi_cnt         += c.pi_cnt

        res = 0

        if self._kukjin_as_doublepi and has_kukjin:
            pi_cnt += 2
            animal_cnt -= 1

        if pi_cnt >= 10: res += pi_cnt - 9
        if animal_cnt >= 5 and animal_cnt <= 7: res += animal_cnt - 4
        elif animal_cnt > 7: res += 3
        if bird_cnt == 3: res += 5
        if flag_cnt >= 5: res += flag_cnt - 4

        if light_cnt == 3 and sublight: res += 2
        elif light_cnt == 3 and not sublight: res += 3
        elif light_cnt == 4: res += 4
        elif light_cnt == 5: res += 15

        if red_flag_cnt == 3: res += 3
        if blue_flag_cnt == 3: res += 3
        if plane_flag_cnt >= 3: res += 3

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
            cnt += 1 if c.is_light else 0
        return cnt == 0

class GameState(Enum):
    ClaimPresident = 1


class Game(object):
    _turn_cnt = 0
    _players = None
    _deck = None
    _board = None
    _question = None

    @property
    def num_player(self):
        return len(self._players)

    @property
    def goable_score(self):
        if self.num_player == 2: return 7
        elif self.num_player == 3: return 3

    def __init__(self, num_players:int=2):
        if num_players == 2:
            num_hand = 10
            num_board = 8
        elif num_players == 3:
            num_hand = 7
            num_board = 6
        else: raise NotImplemented

        need_init = True
        self._turn_cnt = 0

        while need_init:
            need_init = False
            self._players = list()
            self._deck = list()
            self._board = set()

            for _ in range(num_players):
                self._players.append(Player())

            for i in range(1, Card.Bomb):
                self._deck.append(Card(i))

            random.shuffle(self._deck)
            for i in range(self.num_player):
                hand, self._deck = self._deck[:num_hand], self._deck[num_hand:]
                self._players[i]._hand.update(hand)

            board, self._deck = self._deck[:num_board], self._deck[num_board:]
            self._board.update(board)

            for c in self._board: #type: Card
                if c.is_bonus:
                    self._board.remove(c)
                    self._players[0]._acquired(c)

            # check president for the cards on the board
            cnt = dict()
            for c in self._board: #type:Card
                m = c.month
                cnt[m] = cnt.get(m, 0) + 1

            res = []
            for k in cnt.keys():
                if cnt[k] == 4:
                    need_init = True
                    break

