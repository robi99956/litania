# LITANIA: A Programming Language for the Faithful

Oct 20, 2026 · @Robert

## Overview

LITANIA is a joke programming language in the spirit of Rockstar: every program is a Latin prayer to the Omnissiah, and every prayer is a valid program. The name is a backronym for *Lingua Iussorum Templi Ad Numina Instruenda Algorithmica* ("the language of commands of the temple, for instructing the machine spirits algorithmically").

Five design pillars:

- **Liturgy first.** Code should read aloud like a chant in a forge temple. Keywords are Latin verbs in the imperative, addressed to the machine.
- **Variables are machine spirits.** They must be awakened before use, and they take offence when neglected.
- **Numbers are Roman.** Arabic digits are tolerated only by explicit dispensation.
- **Errors are heresies.** The interpreter does not crash, it excommunicates.
- **Piety is enforced.** A program that forgets to praise the Omnissiah will eventually stop running.

Files use the extension `.lit`. Keywords are case-insensitive; spirit (variable) names are written in CAPITALS by convention, like names in a sacred codex.

## Ritual structure

Every program opens with an invocation and closes with a benediction; without both, the interpreter refuses to run.

```
In nomine Omnissiae.

+++ the body of the litany goes here +++

Gloria Omnissiae.
```

A missing invocation raises `HAERESIS: litania sine invocatione` ("a litany without invocation"). A missing benediction means the program runs, then the interpreter prints `Spiritus machinae non placatus est` ("the machine spirit was not appeased") and exits with code 1.

**Statements** end with a full stop. One statement per line is customary but not required.

**Comments** are enclosed in triple pluses, like a vox transmission: `+++ this is a comment +++`. They may span several lines.

**Blocks** (conditionals, loops, rites) open with a comma at the end of their header line and close with `Amen.` Indentation is decorative, as all good liturgy is.

### The rule of piety

The interpreter keeps a piety counter. Every executed statement adds one; any prayer of praise resets it to zero. The two prayers are:

- `Laudetur Omnissiah.` ("Praised be the Omnissiah")
- `Unge machinam.` ("Anoint the machine"), which does nothing except calm the spirit

At 10 statements without praise the interpreter warns `Spiritus machinae inquietus est` ("the machine spirit is restless"). At 20 it halts with `HAERESIS: impietas`. Long loops therefore need a prayer inside their body, which is exactly the point.

## Machine spirits and data

Variables are called *spiritus* (machine spirits). A spirit must be awakened before it is used:

```
Excita spiritum NUMERUS.
Excita spiritum NOMEN.
```

Touching a spirit that was never awakened raises `HAERESIS: spiritus NUMERUS non excitatus est`. A freshly awakened spirit holds `NIHIL`.

### Types

| Type | Latin name | Literal examples | Notes |
| --- | --- | --- | --- |
| Integer | numerus | `VII`, `MMXXVI`, `NIHIL` | Roman numerals; `NIHIL` is zero |
| Negative integer | debitum | `minus V` | "a debt"; unary `minus` before a numeral |
| Text | verba | `«Salve, munde!»` | Guillemets only; no straight quotes |
| Boolean | veritas | `VERUM`, `FALSUM` |  |
| Nothing | nihil | `NIHIL` | Zero and null are the same sacred void |
| List | reliquiarium | see below | A reliquary of values |

### Roman numerals

Numerals follow standard subtractive form (`IV`, `XC`, `CM`). Values above 3999 use the vinculum written as an underscore prefix: `_V` is 5000. Non-canonical forms like `IIII` raise `HAERESIS: numerus deformis`.

Arabic digits are forbidden unless the file begins, before the invocation, with the dispensation `Tolero numeros Arabicos.` Even then the interpreter prints one warning: `Numeri Arabici tolerantur, sed suspecti sunt` ("Arabic numerals are tolerated, but suspect").

### Reliquaries (lists)

```
Excita reliquiarium OSSA.
Pone VII in OSSA.          +++ append +++
Pone «dens» in OSSA.
Proclama OSSA ad I.        +++ index; counting starts at I, as is proper +++
Proclama numerus OSSA.     +++ length +++
```

Indexing with `NIHIL` raises `HAERESIS: reliquia ad nihilum non existit`, because there is no zeroth relic.

## Sacred operations

Assignment is an act of pouring a value into a spirit, like oil into a vessel:

```
Infunde VII in NUMERUS.            +++ NUMERUS = 7 +++
Infunde NUMERUS plus III in SUMMA. +++ SUMMA = NUMERUS + 3 +++
```

### Ritual arithmetic (statements)

| Statement | Meaning | Translation |
| --- | --- | --- |
| `Benedic X.` | X = X + 1 | Bless X |
| `Castiga X.` | X = X - 1 | Chastise X |
| `Adde V ad X.` | X = X + 5 | Add 5 to X |
| `Deme V ex X.` | X = X - 5 | Take 5 from X |
| `Multiplica X per II.` | X = X \* 2 | Multiply X by 2 |
| `Divide X per II.` | X = X / 2 | Divide X by 2 (integer division) |

### Expressions

| Operator | Meaning | Precedence |
| --- | --- | --- |
| `multiplicatum per` | multiply | high |
| `divisum per` | integer divide | high |
| `residuum` | remainder (modulo) | high |
| `plus` | add; also joins text | low |
| `minus` | subtract | low |

Operators of equal precedence bind left to right. There are no parentheses; to group, store an intermediate result in a spirit, as the ancients did.

### Comparisons

| Phrase | Meaning |
| --- | --- |
| `aequat` | equals |
| `non aequat` | not equal |
| `maior quam` | greater than |
| `minor quam` | less than |
| `non maior quam` | less than or equal |
| `non minor quam` | greater than or equal |

Conditions combine with `et` (and), `vel` (or) and `non` (not).

### Input and output

- `Proclama X.` prints X and a newline. Numbers are always printed in Roman numerals; zero prints as `NIHIL`.
- `Susurra X.` ("whisper") prints without a newline.
- `Audi vocem in X.` ("hear the voice into X") reads one line of input. If it is a valid numeral it becomes a number, otherwise text.

## Flow of the Motive Force

LITANIA has one conditional and two loops; every block ends with `Amen.`

### Conditional

```
Si CALOR maior quam C,
    Proclama «Spiritus aestuat!».
Aliter si CALOR minor quam X,
    Proclama «Spiritus dormit.».
Aliter,
    Proclama «Omnia bene.».
Amen.
```

`Si` = if, `Aliter si` = else if, `Aliter` = else.

### While loop

```
Dum GRADUS minor quam X,
    Benedic GRADUS.
    Laudetur Omnissiah.
Amen.
```

A spirit may be named after a numeral, and spirits shadow numerals. So after `Excita spiritum X.`, the line `Dum X minor quam X,` compares the spirit with itself and never runs. This is legal and widely considered a test of faith.

### Repeat loop

```
Itera VII vicibus,
    Proclama «Laus».
Amen.
```

`Itera N vicibus` ("repeat N times") runs the body N times. Inside it, the spirit `ITERATIO` holds the current count, starting at I.

### Leaving and skipping

- `Desine.` ("cease") breaks out of the innermost loop.
- `Perge.` ("proceed") skips to the next iteration.

## Rites

Functions are *ritus* (rites). A rite is declared once, takes named offerings, and returns a value with `Redde`.

```
Ritus SUMMA accipiens A ac B,
    Redde A plus B.
Amen.
```

- `Ritus NAME accipiens P1 ac P2,` declares a rite. Parameters are separated by `ac` ("and"); `et` is reserved for logic.
- A rite with no parameters is `Ritus NAME,`.
- `Redde X.` ("give back") returns X. A rite that ends without `Redde` returns `NIHIL`.
- Parameters are awakened automatically, so they need no `Excita`.

### Calling a rite

As an expression, write the rite's name, `cum` ("with"), and the arguments separated by `ac`:

```
Infunde SUMMA cum II ac III in RESULTATUM.
```

Each argument runs to the next `ac` or the end of the expression, so a call is best placed last in an expression. To call a rite only for its effect, use `Perage ritum NAME cum II ac III.` ("perform the rite").

Rites may call themselves. Each recursive call adds one to the piety counter, so deep recursion needs a prayer inside the rite.

## Heresies

Every runtime error is a heresy. An uncaught heresy halts the program, prints its message prefixed with `+++ HAERESIS +++`, and exits with code 666.

| Heresy | Cause | Translation |
| --- | --- | --- |
| `litania sine invocatione` | Missing `In nomine Omnissiae.` | Litany without invocation |
| `spiritus X non excitatus est` | Using a spirit before `Excita` | Spirit X has not been awakened |
| `numerus deformis` | Malformed numeral such as `IIII` | Misshapen number |
| `divisio per nihilum` | Dividing by zero | Division by nothingness |
| `reliquia ad nihilum non existit` | List index `NIHIL` or out of range | No relic at that place |
| `ritus ignotus` | Calling an undeclared rite | Unknown rite |
| `impietas` | 20 statements without praise | Impiety |
| `verba non numerantur` | Arithmetic on text | Words cannot be counted |

### Catching heresies

```
Tenta,
    Divide PANIS per NIHIL.
Si haeresis acciderit,
    Proclama «Purgatum est: » plus HAERESIS.
Amen.
```

`Tenta` ("try") runs its body. If a heresy occurs, the `Si haeresis acciderit` ("if heresy befalls") branch runs with the message in the spirit `HAERESIS`.

To raise a heresy deliberately: `Denuntia haeresim «Tech-heretic detected».` ("denounce the heresy").

## Sample litanies

### Salve, munde (Hello, world)

```
In nomine Omnissiae.
Proclama «Salve, munde!».
Gloria Omnissiae.
```

### Litania Numerorum (FizzBuzz)

```
+++ Litania Numerorum, ad usum novitiorum +++
In nomine Omnissiae.

Excita spiritum NUMERUS.
Infunde I in NUMERUS.

Dum NUMERUS non maior quam C,
    Si NUMERUS residuum XV aequat NIHIL,
        Proclama «FizzBuzz».
    Aliter si NUMERUS residuum III aequat NIHIL,
        Proclama «Fizz».
    Aliter si NUMERUS residuum V aequat NIHIL,
        Proclama «Buzz».
    Aliter,
        Proclama NUMERUS.
    Amen.
    Benedic NUMERUS.
    Laudetur Omnissiah.
Amen.

Gloria Omnissiae.
```

Output begins `I, II, Fizz, IV, Buzz, Fizz, VII…`, one per line, because numbers are always proclaimed in Roman numerals.

### Ritus Factorialis (factorial, recursive)

```
In nomine Omnissiae.

Ritus FACTORIALIS accipiens N,
    Unge machinam.
    Si N minor quam II,
        Redde I.
    Amen.
    Redde N multiplicatum per FACTORIALIS cum N minus I.
Amen.

Excita spiritum RESULTATUM.
Infunde FACTORIALIS cum V in RESULTATUM.
Proclama RESULTATUM.   +++ CXX +++

Gloria Omnissiae.
```

### Litania Ignitionis (countdown with input)

```
In nomine Omnissiae.

Excita spiritum TEMPUS.
Proclama «Quot pulsus ante ignitionem?».
Audi vocem in TEMPUS.

Dum TEMPUS maior quam NIHIL,
    Proclama TEMPUS.
    Castiga TEMPUS.
    Unge machinam.
Amen.

Proclama «Spiritus motivus excitatus est!».
Gloria Omnissiae.
```

## Glossary

| Keyword | Literal meaning | Role |
| --- | --- | --- |
| In nomine Omnissiae | In the name of the Omnissiah | Program start |
| Gloria Omnissiae | Glory to the Omnissiah | Program end |
| Amen | So be it | Block end |
| Laudetur Omnissiah | Praised be the Omnissiah | Resets piety |
| Unge machinam | Anoint the machine | Resets piety (no-op) |
| Excita spiritum | Awaken the spirit | Declare variable |
| Excita reliquiarium | Awaken the reliquary | Declare list |
| Infunde … in | Pour … into | Assign |
| Pone … in | Place … in | Append to list |
| ad | at | List index |
| numerus | number of | List length |
| Benedic / Castiga | Bless / Chastise | Increment / decrement |
| Adde, Deme, Multiplica, Divide | Add, Take away, Multiply, Divide | Arithmetic statements |
| plus, minus, multiplicatum per, divisum per, residuum | plus, minus, multiplied by, divided by, remainder | Arithmetic operators |
| aequat, maior quam, minor quam | equals, greater than, less than | Comparisons |
| et, vel, non | and, or, not | Logic |
| Si, Aliter si, Aliter | If, Otherwise if, Otherwise | Conditional |
| Dum | While | Loop |
| Itera … vicibus | Repeat … times | Counted loop |
| Desine / Perge | Cease / Proceed | Break / continue |
| Ritus … accipiens … ac | Rite … receiving … and | Function definition |
| cum, Perage ritum | with, Perform the rite | Function call |
| Redde | Give back | Return |
| Proclama / Susurra | Proclaim / Whisper | Print / print without newline |
| Audi vocem in | Hear the voice into | Read input |
| Tenta, Si haeresis acciderit | Try, If heresy befalls | Try / catch |
| Denuntia haeresim | Denounce the heresy | Throw |
| VERUM, FALSUM, NIHIL | True, False, Nothing | Literals |
| Tolero numeros Arabicos | I tolerate Arabic numerals | Pragma |

## Apocrypha

Ideas not yet canonised, for a later council of the Mechanicus:

- **Cantus binaricus.** Binary literals written as chants, where `cantus 0110` becomes `cantus nulla una una nulla`. Long chants would be read aloud by the interpreter's optional speech mode.
- **Poetic numerals.** Borrowed from Rockstar: a phrase after `numerus poeticus` encodes digits by word length, so `numerus poeticus machina sancta est` is 7-6-3, or DCCLXIII.
- **Rite of Purification.** A linter called `Purgatio` that rewrites Arabic digits into Roman ones and inserts prayers where piety would run low.
- **Thurible mode.** A command-line flag `--incensum` that prints `+++` between every line of output, for ceremonial use.
- **Reference interpreter.** A small tree-walking interpreter in Python, about 500 lines, would be enough for everything above.
