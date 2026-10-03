# Bot and Credential-Stuffing Detector

**Author:** Deepak S

A small, self-contained lab that simulates a login service, generates both human and attacker traffic against it, and trains a machine-learning model to tell them apart. The focus is not the final accuracy score but the **attacker vs. defender loop**: each model version was broken by a new kind of attacker, the cause was diagnosed, and the next version was built to address it.

> All traffic is simulated against a Flask app running on `localhost`. No real sites, accounts, or leaked data are involved.

## Why this project

Credential stuffing (replaying leaked username/password pairs at login pages) and bot abuse are among the most common web attacks. Defending against them is hard because a single request looks normal, and a good attacker spreads activity across many identities so that no single visitor looks suspicious. This project reproduces that dynamic at small scale.

## How it works

1. **Login service** (`app.py`): a Flask app with three accounts. Every login attempt is written to `logs/notebook.txt` as one JSON line (time, visitor ID, username tried, success, browser, language).
2. **Traffic simulators**: scripts that act as humans and as bots, each tagged with a visitor ID (`X-Client-ID` header) so ground truth is known.
3. **Feature extraction** (`features.py`): groups log lines into visits (a gap of more than 30 seconds starts a new visit) and computes per-visit features.
4. **Model** (`train.py`): a Random Forest, evaluated with a split **by visitor** so the same visitor never appears in both training and test data, plus 5-fold grouped cross-validation.

### Features

| Feature | Meaning |
|---|---|
| `total_requests` | Login attempts in the visit |
| `failed_ratio` | Share of attempts that failed |
| `unique_usernames` | Distinct usernames tried |
| `invalid_username_ratio` | Share of attempts using a username that does not exist |
| `other_failers_same_username` | Other visitors who failed on the same username within 5 minutes |
| `avg_gap_sec`, `gap_std_sec` | Mean and spread of time between attempts (robotic timing has near-zero spread) |
| `missing_language`, `script_browser` | No language header; scripting-library user agent |

The visitor name and visitor type are never given to the model.

### Simulated visitors

| Type | Behaviour |
|---|---|
| `human-normal` | One login, occasionally a typo first |
| `human-forgetful` | Several wrong passwords, then success |
| `human-repeat` | Several successful logins in one visit |
| `human-office` | Several users behind one shared network ID |
| `human-giveup` | A few wrong passwords, then leaves |
| `human-wrongname` | Mistypes the username, then succeeds |
| `bot-fast` | No delay, script user agent, many usernames |
| `bot-disguised` | Browser user agent, fixed 0.5 s delay |
| `bot-slow` | Browser user agent, random human-like delays |
| `bot-spread` | 150 throwaway identities, 2 to 3 attempts each, made-up usernames |
| `bot-valid` | 150 throwaway identities, 2 to 3 attempts each, **real usernames**, old passwords |
| `bot-small` | Same as `bot-valid` but only 20 identities |

## Results

| Version | What changed | Outcome |
|---|---|---|
| **v1** | Trained on fast, disguised and slow bots vs. humans | Perfect score on its own test set. Caught **0 of 150** `bot-spread` visits. It had learned "many requests with many failures is a bot", and each spread bot made only 2 or 3 attempts. |
| **v2** | Added `bot-spread` to training | Caught the spread bots, but wrongly flagged **30 of 40** `human-giveup` and 4 of 15 `human-wrongname` visits. Top feature was `failed_ratio`: the model had learned "never gets in means bot". |
| **v3** | Added `human-giveup`, `human-wrongname`, more `human-office`, and `invalid_username_ratio` | 0 humans wrongly blocked and 1 of 150 spread bots missed in grouped cross-validation. Then missed **150 of 150** `bot-valid` visits: with real usernames, its best feature drops to zero. |
| **v4** | Added `other_failers_same_username` (cross-visitor feature) | 100% on its held-out test set, 5-round grouped CV average 0.998, `bot-valid` caught (37 of 37 in the test split). Then missed **20 of 20** `bot-small` visits. |

### v4 grouped cross-validation (all visits)

Every visit is predicted while its own visitor is held out of training, using all features. Visitors are never split across folds, but other visitors from the same attack type can be in the training folds.

| Visitor type | Wrong | Total |
|---|---|---|
| bot-disguised | 0 | 20 |
| bot-fast | 0 | 40 |
| bot-slow | 0 | 24 |
| bot-small | 2 | 20 |
| bot-spread | 1 | 150 |
| bot-valid | 0 | 150 |
| human-forgetful | 0 | 18 |
| human-giveup | 3 | 40 |
| human-normal | 0 | 50 |
| human-office | 0 | 21 |
| human-repeat | 0 | 24 |
| human-wrongname | 0 | 15 |

**3 humans wrongly blocked (all `human-giveup`) and 3 bots missed**, out of 552 visits.

This table and the miss on `bot-small` above answer different questions. Cross-validation asks whether the model can recognise an attack type it has seen examples of. The `bot-small` test asked whether v4, trained before that attack existed, could detect it. It could not. Once examples of the small attack are in the training data, the model separates most of them, so the two attack sizes are distinguishable, but only after training on that attack.

### What the v4 failure showed

For `other_failers_same_username`:

| Group | Mean | Range |
|---|---|---|
| `bot-valid` (150 bots) | 51.3 | 39 to 64 |
| `bot-small` (20 bots) | 6.9 | 2 to 9 |
| All human types | 8.5 to 17.4 | 1 to 23 |

Every human type tops out at 23 and the large attack starts at 39, so the model effectively learned "more than about 25 means bot". The small attack sits at the bottom of the human range, so this feature alone cannot flag it. On the other features it looks much like `human-giveup` (2 to 3 requests, mostly failures, one valid username, normal browser), which is why v4 missed all 20 when it had never seen that attack. It is not fully indistinguishable: once trained on examples of it, the cross-validated model separates all but 2 of 20, at the cost of 3 wrongly blocked `human-giveup` visits out of 40. The exact signal it uses for this was not investigated.

## Limitations

- **Simulated data.** Humans and bots are generated by scripts I wrote, so near-perfect scores mainly reflect how different the simulated groups are, not real-world performance.
- **Only three accounts.** Every simulated human uses `alice`, `bob` or `carol`, so normal accounts see many failures in any 5-minute window. This inflates the human baseline for `other_failers_same_username`. On a site with many accounts, a normal account would see close to zero failures and a small coordinated attack would stand out far more. This is untested here.
- **The cross-visitor feature partly measures how busy the accounts were.** The fast, disguised and slow bots average about 18 on it even though they were not coordinating; they overlapped in time with the humans. Those bots are still caught by their other features.
- **Small test groups.** Some human types contributed only a handful of visitors to a given test split (for example 2 `human-office` visitors in the v4 split). Cross-validation is a better guide than any single split.
- **Attack-size dependence.** Trained without small-attack examples, v4 detects a 150-bot attack and not a 20-bot attack from the same attacker.
- **Cross-validation is optimistic about new attacks.** Each fold still contains other visitors from the same attack type, so those scores show recognition of known attacks, not generalisation to unseen ones. The held-out-attack tests (v1 on `bot-spread`, v3 on `bot-valid`, v4 on `bot-small`) are the better measure of that, and all three failed.
- **A tradeoff remains.** v4 in cross-validation blocks 3 of 40 `human-giveup` visits while missing 2 of 20 small-attack bots.
- **Visit splitting.** A 30-second gap starts a new visit, so a few visitors appear as more than one row.

## Takeaways

1. A model can score 100% and still fail completely against an attacker it was not trained on. Held-out accuracy only measures resemblance to the training data.
2. Per-visitor features alone cannot catch a well-distributed attack; the attack only exists at the level of the whole population of visitors.
3. Every blunt feature has a human cost. v2 caught more bots by treating "never succeeds" as suspicious, and as a result blocked most people who simply gave up.
4. A small, quiet attack with valid usernames needs a baseline of normal behaviour per account, plus other signals such as IP reputation or device fingerprints. This is why production systems combine many signals rather than relying on one model.

## Future work

- Create a few hundred accounts and spread the human traffic across them, then re-test the small attack to see whether a per-account baseline separates it.
- Add a per-account feature: the share of attempts on an account in the last few minutes that failed.
- Train on attacks of several sizes and test on an unseen size.
- Add a simple rate limiter and measure how many bot attempts it blocks against how many humans it delays.
- Add a Streamlit dashboard for live traffic.

## Running it

```
pip install flask requests pandas scikit-learn joblib

python app.py                 # terminal 1: the login service

# terminal 2: generate traffic (wait at least a minute between runs)
python normal_users.py
python bots.py
python spread_bot.py
python giveup_humans.py
python valid_bot.py

python features.py            # build features.csv
python train.py               # train and evaluate
python compare_models.py      # grouped cross-validated error table
```

Wait at least 6 minutes after any run before generating a new attack when you plan to test a model against it, because `other_failers_same_username` looks at the 5 minutes around each visit.

## Tech

Python 3.12, Flask, pandas, scikit-learn (Random Forest, grouped splits), joblib.
