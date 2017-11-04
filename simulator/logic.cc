#include <cstdio>
#include <cstdlib>

#include <assert.h>

#include <cstring>
#include <set>
#include <array>
#include <vector>
#include <random>
#include <algorithm>

/*
 * Gostop/Matgo (Korean Hanahuda)
 * simulator
 */

using namespace std;


class Card
{

public:
    enum CardType:int {
        // Please see https://namu.wiki/w/%ED%99%94%ED%88%AC/%ED%8C%A8 
        // Following cards are defined in the same order as appeared in the above link

        JanLight,  JanRedFlag,  Jan1,    Jan2,
        FebBird,   FebRedFlag,  Feb1,    Feb2,
        MarLight,  MarRedFlag,  Mar1,    Mar2,
        AprBird,   AprFlag,     Apr1,    Apr2,
        MayBridge, MayFlag,     May1,    May2,
        Jun1,      JunBlueFlag, Jun2,    Jun3,
        JulPig,    JulFlag,     Jul1,    Jul2,
        AugLight,  AugBird,     Aug1,    Aug2,
        SepFlask,  SepBlueFlag, Sep1,    Sep2,
        OctDeer,   OctBlueFlag, Oct1,    Oct2,
        NovLight,  NovDouble,   Nov1,    Nov2,
        DecLight,  DecBird,     DecFlag, DecDoor,

        // bonus cards
        JokerDouble1, 
        JokerDouble2,
        JokerTriple,
        
        // virtual cards
        Bomb,
        EndCardType
    };

    struct Properties {
        int  score;        // value as a Pi (0-not a pi, 1-pi, 2-ssang pi, 3-three pi)
        bool light;        // gwang
        bool sub_light;    // bi gwang
        bool animal;       // ggeut
        bool bird;         // godori
        bool flag;         // cho dan, a flag with no chracters on it
        bool blue_flag;    // chung dan
        bool red_flag;     // hong dan
        bool bomb;
        bool joker;

        int month;
    };

protected:
    static Properties props_[CardType::EndCardType];
    CardType type_;


public:

    Card(CardType type):type_(type) { }
    inline CardType type() { return type_; }

    inline bool matched(const Card& other) {
        int my_month = month();

        if (1 <= my_month && my_month <= 12) {
            int your_month = other.month();
            return (my_month == your_month);
        }

        return false;
    }

    inline int month() const { return props_[type_].month; }
    inline const Properties& prop() const { return props_[type_]; }

    inline bool operator<  (const Card& b) const { return type_ < b.type_; }
    inline bool operator== (const Card& b) const { return type_ == b.type_; }
    inline bool operator>  (const Card& b) const { return type_ > b.type_; }
};

/*
 * The basic model of game.
 * 
 * The game object is a dealer that operates the whole process.
 *
 * For each turn, the game object asks questions to the player objects, which action will the players take.
 * As the game object does not call callbacks, the player objects should call question() method to get the question.
 * 
 * If the question is turned out to be related to the player that called the method,
 * the player object should call action() method to notice its decision to the game object, and to proceed the game.
 *
 */


class Game
{
public:
    enum Question: int
    {
        ClaimPresident, 
        WhichCardToThrow,
        PickFromDeck,
        WhichCardToPick,
        UseAsDoublePi,  // "국진을 쌍피로?"
        SayGo,
    };

    struct Answer
    {
        std::set<Card> cards;
        bool shake;
        bool bomb;
        bool yesno;
    };

    struct Player {
        std::set<Card> hand;
        std::set<Card> acquired;
        std::set<Card> exposed;
        int cnt_go;
        int cnt_shake;
        bool use_as_double_pi;

        Player() {
            cnt_go = 0;
            cnt_shake = 0;
            use_as_double_pi = false;
        }

        inline int cnt_light() const {
            int res = 0;
            for (auto it=acquired.cbegin(); it!=acquired.cend(); it++)
                if (it->prop().light) res ++;
            return res;
        }

        inline bool has_sublight() const {
            return acquired.find(Card(Card::CardType::DecLight)) != acquired.cend();
        }

        inline int cnt_pi_score() const {
            int res = 0;
            for (auto it=acquired.cbegin(); it!=acquired.cend(); it++)
                res += it->prop().score;
            if (use_as_double_pi && acquired.find(Card(Card::CardType::SepFlask)) != acquired.cend())
                res += 2;
            return res;
        }

        inline int cnt_animal() const { // 열끗 
            int res = 0;
            for (auto it=acquired.cbegin(); it!=acquired.cend(); it++)
                if (it->prop().animal) res ++;
            if (use_as_double_pi && acquired.find(Card(Card::CardType::SepFlask)) != acquired.cend())
                res -= 1;
            return res;
        }

        inline bool cnt_president() const { 
            int month_cnt[12];
            int res = 0;
            memset(month_cnt, 0, sizeof(month_cnt));

            for (auto it = hand.cbegin(); it != hand.cend(); it++) {
                int cur_month = it->prop().month;
                if (cur_month > 0 && cur_month <= 12)
                    month_cnt[cur_month-1]++;
            }

            for (int i=0; i<12; i++)
                if (month_cnt[i] == 4) res++;

            return res;
        }

        inline int month_count (int month) const {
            int cnt = 0;
            for (auto it = hand.cbegin(); it != hand.cend(); it++)
                if (it->prop().month == month) cnt++;
            return cnt;
        }

        inline bool completed_red_flags() const {
            if (acquired.find(Card(CardType::JanRedFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::FebRedFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::MarRedFlag) == acquired.cend()) return false;
            return true;
        }

        inline bool completed_blue_flags() const {
            if (acquired.find(Card(CardType::JunBlueFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::SepBlueFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::OctBlueFlag) == acquired.cend()) return false;
            return true;
        }

        inline bool completed_flags() const {
            if (acquired.find(Card(CardType::AprFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::MayFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::JulFlag) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::DecFlag) == acquired.cend()) return false;
            return true;
        }

        inline bool completed_five_bird() const {
            if (acquired.find(Card(CardType::FebBird) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::AprBird) == acquired.cend()) return false;
            if (acquired.find(Card(CardType::AugBird) == acquired.cend()) return false;
            return true;
        }

        inline void transfer_score_card(Player& other) {
            if (hand.size() == 0) return;
            else {
                auto selected_it = hand.begin();
                int selected_score = -1;
                for (auto it=hand.begin(); it!=hand.end(); it++) {
                    int cur_score = it->prop().score;
                    if (cur_score == 0) continue;
                    if (selected_score == -1 || selected_score > cur_score) {
                        selected_score = cur_score;
                        selected_it = it;
                        if (selected_score == 1) break;
                    }
                }

                if (selected_score > 0) {
                    other.hand.insert(*selected_it);
                    hand.erase(seleceted_it);
                }
            }
        }
    };

protected:
    std::vector<Player>            players_;
    std::set<Card>                 board_;
    std::vector<Card>              deck_;
    std::set<Card>                 player_thrown_;
    int                            leader_; // who is currently leading go/stop
    int                            turn_;
    bool                           end_;

    std::mt19937                   rndgen_;
    std::random_device             rnddev_;

    Question                       question_;

    inline int count_cards(std::set<Card> cardpile, int month) {
        int count = 0;
        for (auto it=pile.begin(); it!=pile.end(); it++)
            if (it->prop().month == month) count ++;
        return count;
    }

public:
    Game(int num_players);
    Game(const Game& game);

    std::string serialize() const;
    void restore(const std::string& data);

    inline Question question() const { return question_; }
    inline int turn() const { return turn_; }
    inline bool end() const { return end_; }
    inline int winner() const { return (end_) ? leader_: -1; }

    bool answer(int player, const Answer& action); 
    int  score(int player) const;
    void shuffle_invisible();

    PlayerSight status(int player) const;
    Question question() const;
};

Game::Game(int num_players)
: rnddev_(), rndgen_(rnddev_()),
{

    num_players_ = num_players;

    turn_cnt_ = 0;
    turn_ = 0;
    go_authority_ = 0;
    done_ = false;

    go_count_.resize(num_players);
    score_.resize(num_players);
    booster_.resize(num_players, 1);

    // currently we only support the 2 player game
    // this restriction will be removed someday.
    assert(num_players_ == 2);
    assert(num_players_ == 2 || num_players_ == 3);

    cards_in_hand_.resize(num_players_);
    cards_acquired_.resize(num_players_);
    turn_ = 0;

    // initialize the deck
    for (int i=0; i< static_cast<int>(Card::CardType::Bomb); i++)
        deck_.push_back(Card(static_cast<Card::CardType>(i)));

    shuffle_deck();

    // deal out cards
    int num_card_per_player = (num_players_ == 2)? 10: 7;
    int num_card_on_board   = (num_players_ == 2)? 8:  6;

    for (int pidx=0; pidx < num_players_; pidx++) {
        for (int i=0; i<num_card_per_player; i++) {
            cards_in_hand_[pidx].insert(deck_.back());
            deck_.pop_back();
        }
    }

    for (int i=0; i<num_card_on_board; i++) {
        cards_on_board_.insert(deck_.back());
        deck_.pop_back();
    }

    // give all jokers on the board to the first player
    for(auto it=cards_on_board_.begin(); it != cards_on_board_.end();)
    {
        if (it->prop().joker) {
            cards_in_hand_[0].insert(*it);
            cards_on_board_.erase(it);
        }
        else it++;
    }

    // check whether "president" occured on the board
    int month_count[13];
    memset(month_count, 0, sizeof(month_count));
    for (auto it=cards_on_board_.begin(); it!=cards_on_board_.end(); it++)
        month_count[it->prop().month]++;
    for (int i=1; i<13; i++) {
        // if a set of cards of the same month found on the board
        if (month_count[i] == 4) {
            // consider the first player as the winner
            done_ = true;
            score_[0] = 3;
            go_authority_ = 0;
        }
    }
}

void Game::shuffle_deck()
{
    std::shuffle(deck_.begin(), deck_.end(), rndgen_);
}

bool Game::check_president(int player, Card card)
{
    int month_count;
    int month = card.prop().month;
    month_count = count_cards_by_month(cards_in_hand_[player], month);

    return (month_count == 4) && (month >= 1 && month <= 12);
}

void Game::process_president(int player, Card card, bool say_go)
{
    int president_month = card.prop().month;

    score_[player] += 3;
    if (action.say_stop) done_ = true;
    else {
        booster_[player] *= 4; // shake + bomb applied
        bomb_[player] += 3;

        std::set<Card>& hand = cards_in_hand_[player];
        std::set<Card>& acquired = cards_acquired_[player];
        for (auto it=hand.begin(); it!=hand.end(); it++) {
            if (it->prop().month == president_month) {
                acquired.insert(*it);
                hand.erase(it);
            }
            else it++;
        }
    }
}

bool Game::check_shakable(int player, Card card)
{
    int month_in_hand, month_on_board;
    int month = card.prop().month;
    month_in_hand  = count_cards_by_month(cards_in_hand_[player], month);
    month_on_board = count_cards_by_month(cards_on_board_, month);
    return (month_in_hand == 3) && (month_on_board == 0);
}

bool Game::check_bomb(int player, Card card)
{
    int month_in_hand, month_on_board;
    int month = card.prop().month;
    month_in_hand  = count_cards_by_month(cards_in_hand_[player], month);
    month_on_board = count_cards_by_month(cards_on_board_, month);

    return (month_in_hand == 3 || month_in_hand == 2)
        && (month_in_hand + month_on_board == 4);
}

void Game::process_bomb(int player, Card card)
{
    int month_in_hand, month_on_board;
    int month = card.prop().month;

    month_in_hand  = count_cards_by_month(cards_in_hand_[player], month);
    month_on_board = count_cards_by_month(cards_on_board_, month);

    bomb_[player] += (month_in_hand - 1);
}

bool Game::throw_cards(int player, std::set<Card> hand)
{
    if (hand.size() < 1) return false;
    int month = hand.begin()->prop().month;

    bool hands_agree = true;
    for (auto it=hand.begin(); it!=hand.end(); it++) {
        if (it->prop().month != month) {
            hands_agree = false;
            break;
        }

        if (cards_in_hand_[player].find(*it) == cards_in_hand_[player].end()) {
            hands_agree = false;
            break;
        }
    }
    if (!hands_agree) return false;
    if (!target.prop().month != month) return false;
    if (cards_on_board_.find(target) == cards_on_board_.end()) return false;

    if (hand.size() == 1)
    {
        cards_on_board_.erase(cards_on_board_.find(target));
        cards_acquired_[player].insert(target);
    }
}


bool Game::action(int player, const Game::Action& action)
{
    // basic validity check
    if(!(player >= 0 && player < num_players_)) return false;
    if (done_) return false;

    switch(state_)
    {
        case ClaimPresident:
        break;
        case WhichCardToThrow:
        break;
        case PickFromDeck:
        break;
        case WhichCardToPick:
        break;
    }

    // Following actions can be taken by the player of current turn.
    if (player != turn_) return false;

    bool card_used = false;

    if (!card_used) {
        // use bomb card
        if (action.card.prop().bomb) {
            // the player has to own bomb cards
            if (bomb_[player] < 1) return false;
            card_used = true;
        }
    }

    if (!card_used) {
        // all following cases require action.card is included in the player's hand.
        if (cards_in_hand_[player].find(action.card) == cards_in_hand_.end())
            return false;

        if (action.bomb) {
            // check for validity
            int month = Card(action.card).prop();
            if (!(1 <= month && month <= 12)) return false;
            int my_hnad = 0;
            int board = 0;
            for (auto it=cards_on_board_.begin(); it=cards_on_board_.end(); it++)
                if (it->prop().month == month) board++;
            for (auto it=cards_in_hand_[player].begin(); it!=cards_in_hand_[player].end(); it++)
                if (it->prop().month == month) my_hand ++;

            bool valid_bomb = (my_hand >=2 && (my_hand+board) == 4);
            if (!valid_bomb) return false;

            for (auto it=
        }
    }

    return true;
}

int Game::score(int player) const
{
    return 0;
}

Game::Game(const Game& game)
{
}

std::string Game::serialize() const
{
    return "";
}

void Game::restore(const std::string& data)
{
}

Game::PlayerSight Game::status(int player) const
{
    PlayerSight res;
    return res;
}


Card::Properties Card::props_[Card::CardType::EndCardType] = 
{   
    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  0,     true,  false,    false, false, false, false,    false,   false, false, 1  }, // JanLight
    {  0,     false, false,    false, false, false, false,    true,    false, false, 1  }, // JanRedFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 1  }, // Jan1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 1  }, // Jan2
                                                                                       
    {  0,     false, false,    true,  true,  false, false,    false,   false, false, 2  }, // FebBird
    {  0,     false, false,    false, false, false, false,    true,    false, false, 2  }, // FebRedFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 2  }, // Feb1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 2  }, // Feb2
                                                                                       
    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  0,     true,  false,    false, false, false, false,    false,   false, false, 3  }, // MarLight
    {  0,     false, false,    false, false, false, false,    true,    false, false, 3  }, // MarRedFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 3  }, // Mar1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 3  }, // Mar2
                                                                                
    {  0,     false, false,    true,  true,  false, false,    false,   false, false, 4  }, // AprBird
    {  0,     false, false,    false, false, true,  false,    false,   false, false, 4  }, // AprFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 4  }, // Apr1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 4  }, // Apr2
                                                                                       
    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  0,     false, false,    true,  false, false, false,    false,   false, false, 5  }, // MayBridge
    {  0,     false, false,    false, false, true,  false,    false,   false, false, 5  }, // MayFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 5  }, // May1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 5  }, // May2
                                                                                
    {  0,     false, false,    true,  false, false, false,    false,   false, false, 6  }, // Jun1
    {  0,     false, false,    false, false, false, true,     false,   false, false, 6  }, // JunBlueFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 6  }, // Jun2
    {  1,     false, false,    false, false, false, false,    false,   false, false, 6  }, // Jun3
                                                                                       
    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  0,     false, false,    true,  false, false, false,    false,   false, false, 7  }, // JulPig
    {  0,     false, false,    false, false, true,  false,    false,   false, false, 7  }, // JulFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 7  }, // Jul1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 7  }, // Jul2
                                                                                
    {  0,     true,  false,    false, false, false, false,    false,   false, false, 8  }, // AugLight
    {  0,     false, false,    true,  true,  false, false,    false,   false, false, 8  }, // AugBird
    {  1,     false, false,    false, false, false, false,    false,   false, false, 8  }, // Aug1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 8  }, // Aug2
                                                                                       
    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  0,     true,  false,    true,  false, false, false,    false,   false, false, 9  }, // SepFlask
    {  0,     false, false,    false, false, false, true,     false,   false, false, 9  }, // SepBlueFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 9  }, // Sep1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 9  }, // Sep2
                                                                                
    {  0,     false, false,    true,  false, false, false,    false,   false, false, 10 }, // OctDeer
    {  0,     false, false,    false, false, false, true,     false,   false, false, 10 }, // OctBlueFlag
    {  1,     false, false,    false, false, false, false,    false,   false, false, 10 }, // Oct1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 10 }, // Oct2
                                                                                       
    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  0,     true,  false,    false, false, false, false,    false,   false, false, 11 }, // NovLight
    {  2,     false, false,    false, false, false, false,    false,   false, false, 11 }, // NovDouble
    {  1,     false, false,    false, false, false, false,    false,   false, false, 11 }, // Nov1
    {  1,     false, false,    false, false, false, false,    false,   false, false, 11 }, // Nov2
                                                                                
    {  0,     false, true,     false, false, false, false,    false,   false, false, 12 }, // DecLight
    {  0,     false, false,    true,  false, false, false,    false,   false, false, 12 }, // DecBird
    {  0,     false, false,    false, false, true,  false,    false,   false, false, 12 }, // DecFlag
    {  2,     false, false,    false, false, false, false,    false,   false, false, 12 }, // DecDoor    

    // score  light  sub_light animal bird   flag   blue_flag red_flag bomb   joker  month
    {  2,     false, false,    false, false, false, false,    false,   false, true,  0  }, // Joker double
    {  2,     false, false,    false, false, false, false,    false,   false, true,  0  }, // Joker double
    {  3,     false, false,    false, false, false, false,    false,   false, true,  0  }, // Joker triple

    {  0,     false, false,    false, false, false, false,    false,   true,  false, 0  }  // Bomb
};


int main()
{
    return 0;
}
