#!/usr/bin/env python3
"""
LITANIA - reference interpreter.

    In nomine Omnissiae.

Usage:
    python litania.py program.lit
    python litania.py program.lit --incensum     (ceremonial output mode)

Uses only the Python standard library (Python 3.8+).

Exit codes:
    0    the litany ran and the machine spirit is appeased
    1    the litany ran but lacked "Gloria Omnissiae." at the end
    666  an uncaught heresy (POSIX shells report this as 154, i.e. 666 % 256)

    Gloria Omnissiae.
"""

import argparse
import re
import sys

# ======================================================================
#  Heresies (errors) and control-flow signals
# ======================================================================


class Heresy(Exception):
    """Any LITANIA error, whether found while parsing or while running."""

    def __init__(self, message, line=None):
        super().__init__(message)
        self.message = message
        self.line = line

    def __str__(self):
        if self.line:
            return f"{self.message} (linea {to_roman(self.line)})"
        return self.message


class _Break(Exception):
    """Raised by Desine."""


class _Continue(Exception):
    """Raised by Perge."""


class _Return(Exception):
    """Raised by Redde."""

    def __init__(self, value):
        super().__init__()
        self.value = value


# ======================================================================
#  Roman numerals
#
#  Numbers below 4000 use ordinary subtractive form (IV, XC, MMMCMXCIX).
#  From 4000 up, the thousands are written with a vinculum, shown as an
#  underscore before each letter: _V = 5000, _I_V = 4000, _X_VD = 15500.
#  Each extra underscore multiplies by another 1000.
# ======================================================================

_ROMAN_TABLE = (
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
)
_ROMAN_LETTERS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
_ROMAN_SHAPE = re.compile(r"(?:_*[IVXLCDM])+")
_ROMAN_UNIT = re.compile(r"_*[IVXLCDM]")


def _plain_roman(n):
    parts = []
    for value, symbol in _ROMAN_TABLE:
        count, n = divmod(n, value)
        parts.append(symbol * count)
    return "".join(parts)


def _roman_body(n):
    if n < 4000:
        return _plain_roman(n)
    high, low = divmod(n, 1000)
    return _ROMAN_UNIT.sub(lambda m: "_" + m.group(0), _roman_body(high)) + _plain_roman(low)


def to_roman(n):
    """Render an integer the way the Omnissiah intended."""
    if n == 0:
        return "NIHIL"
    if n < 0:
        return "minus " + to_roman(-n)
    return _roman_body(n)


def looks_roman(word):
    """True if the word is made only of numeral letters (canonical or not)."""
    return bool(_ROMAN_SHAPE.fullmatch(word))


def from_roman(word):
    """Value of a canonical numeral, or None if it is misshapen (e.g. IIII)."""
    values = [
        _ROMAN_LETTERS[unit[-1]] * 1000 ** (len(unit) - 1)
        for unit in _ROMAN_UNIT.findall(word)
    ]
    total = 0
    for i, value in enumerate(values):
        if i + 1 < len(values) and value < values[i + 1]:
            total -= value
        else:
            total += value
    if total <= 0 or _roman_body(total) != word:
        return None
    return total


# ======================================================================
#  Values
#
#  numerus -> int      verba -> str      veritas -> bool
#  reliquiarium -> list
#  NIHIL is the integer 0: zero and null are the same sacred void.
# ======================================================================


def show(value):
    """Text form of a value, as Proclama prints it."""
    if value is True:
        return "VERUM"
    if value is False:
        return "FALSUM"
    if isinstance(value, int):
        return to_roman(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        items = (f"«{x}»" if isinstance(x, str) else show(x) for x in value)
        return "[" + ", ".join(items) + "]"
    return str(value)


def truthy(value):
    return bool(value)


def as_number(value):
    """Insist that a value is a number, or denounce it."""
    if isinstance(value, bool):
        raise Heresy("veritas non numeratur")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        raise Heresy("verba non numerantur")
    if isinstance(value, list):
        raise Heresy("reliquiae non numerantur")
    raise Heresy("typus ignotus")


def values_equal(a, b):
    # Keep VERUM from quietly equalling I, as Python would allow.
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def trunc_div(a, b):
    if b == 0:
        raise Heresy("divisio per nihilum")
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def trunc_mod(a, b):
    return a - b * trunc_div(a, b)


# ======================================================================
#  Lexer
# ======================================================================

WORD, STRING, NUMBER, DOT, COMMA, EOF = "WORD", "STRING", "NUMBER", "DOT", "COMMA", "EOF"


class Token:
    __slots__ = ("kind", "value", "line")

    def __init__(self, kind, value, line):
        self.kind = kind
        self.value = value
        self.line = line

    def describe(self):
        if self.kind == EOF:
            return "finem litaniae"
        if self.kind == DOT:
            return "«.»"
        if self.kind == COMMA:
            return "«,»"
        if self.kind == STRING:
            return f"verba «{self.value}»"
        return f"«{self.value}»"


def lex(source):
    tokens = []
    i, line, n = 0, 1, len(source)
    while i < n:
        c = source[i]
        if c == "\n":
            line += 1
            i += 1
        elif c.isspace():
            i += 1
        elif source.startswith("+++", i):
            end = source.find("+++", i + 3)
            if end < 0:
                raise Heresy("commentarium non clausum", line)
            line += source.count("\n", i, end)
            i = end + 3
        elif c == "«":
            end = source.find("»", i + 1)
            if end < 0:
                raise Heresy("verba non clausa: «» deest", line)
            tokens.append(Token(STRING, source[i + 1:end], line))
            line += source.count("\n", i, end)
            i = end + 1
        elif c in "\"'“”„":
            raise Heresy("verba inter « et » scribenda sunt", line)
        elif c == ".":
            tokens.append(Token(DOT, ".", line))
            i += 1
        elif c == ",":
            tokens.append(Token(COMMA, ",", line))
            i += 1
        elif c.isdigit():
            j = i
            while j < n and source[j].isdigit():
                j += 1
            tokens.append(Token(NUMBER, int(source[i:j]), line))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            tokens.append(Token(WORD, source[i:j], line))
            i = j
        else:
            raise Heresy(f"signum ignotum {c!r}", line)
    tokens.append(Token(EOF, None, line))
    return tokens


# ======================================================================
#  Syntax tree
# ======================================================================


class Node:
    """A statement or expression. `kind` says which; other fields vary."""

    def __init__(self, kind, line, **fields):
        self.kind = kind
        self.line = line
        self.__dict__.update(fields)

    def __repr__(self):
        fields = {k: v for k, v in self.__dict__.items() if k not in ("kind", "line")}
        return f"{self.kind}{fields}"


class Program:
    def __init__(self, body, blessed, allow_arabic):
        self.body = body
        self.blessed = blessed
        self.allow_arabic = allow_arabic


# Words that can never name a spirit or a rite. "haeresis" is deliberately
# absent (the catch handler stores its message in a spirit called HAERESIS),
# and so is "numerus", which is the length operator only when an operand
# follows it, so a spirit may still be called NUMERUS.
RESERVED = {
    "in", "nomine", "omnissiae", "gloria", "amen", "laudetur", "omnissiah",
    "unge", "machinam", "excita", "spiritum", "reliquiarium", "infunde",
    "pone", "ad", "benedic", "castiga", "adde", "deme", "ex",
    "multiplica", "divide", "per", "plus", "minus", "multiplicatum",
    "divisum", "residuum", "aequat", "maior", "minor", "quam", "et", "vel",
    "non", "si", "aliter", "dum", "itera", "vicibus", "desine", "perge",
    "ritus", "accipiens", "ac", "cum", "perage", "ritum", "redde",
    "proclama", "susurra", "audi", "vocem", "tenta", "acciderit",
    "denuntia", "haeresim", "verum", "falsum", "nihil", "tolero",
    "numeros", "arabicos",
}


# ======================================================================
#  Parser (recursive descent)
# ======================================================================


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.allow_arabic = False
        self.loop_depth = 0
        self.rite_depth = 0
        self.no_index = False

    # ---- token helpers ------------------------------------------------

    def peek(self, offset=0):
        return self.tokens[min(self.pos + offset, len(self.tokens) - 1)]

    def advance(self, count=1):
        tok = self.peek()
        for _ in range(count):
            if self.peek().kind != EOF:
                self.pos += 1
        return tok

    def at(self, *words):
        for offset, word in enumerate(words):
            tok = self.peek(offset)
            if tok.kind != WORD or tok.value.lower() != word:
                return False
        return True

    def error(self, expected):
        tok = self.peek()
        raise Heresy(f"syntaxis corrupta: expectabatur {expected}, inventum {tok.describe()}", tok.line)

    def expect_words(self, *words):
        for word in words:
            if not self.at(word):
                self.error(f"«{word}»")
            self.advance()

    def end_statement(self):
        if self.peek().kind != DOT:
            self.error("«.» in fine sententiae")
        self.advance()

    def end_header(self):
        if self.peek().kind != COMMA:
            self.error("«,» in fine capitis")
        self.advance()

    def name(self):
        tok = self.peek()
        if tok.kind != WORD or tok.value.lower() in RESERVED:
            self.error("nomen spiritus vel ritus")
        self.advance()
        return tok.value.upper()

    # ---- program ------------------------------------------------------

    def parse(self):
        if self.at("tolero", "numeros", "arabicos"):
            self.advance(3)
            self.end_statement()
            self.allow_arabic = True

        if not self.at("in", "nomine", "omnissiae"):
            raise Heresy("litania sine invocatione", self.peek().line)
        self.advance(3)
        self.end_statement()

        body = self.block(lambda: self.at("gloria", "omnissiae"), top_level=True)

        blessed = False
        if self.at("gloria", "omnissiae"):
            self.advance(2)
            self.end_statement()
            blessed = True
            if self.peek().kind != EOF:
                raise Heresy("verba post benedictionem", self.peek().line)
        return Program(body, blessed, self.allow_arabic)

    def block(self, is_end, top_level=False):
        statements = []
        while True:
            unclosed = self.peek().kind == EOF or self.at("gloria", "omnissiae")
            if unclosed and not top_level:
                raise Heresy("blocus non clausus: «Amen.» deest", self.peek().line)
            if self.peek().kind == EOF:
                return statements
            if is_end():
                return statements
            statements.append(self.statement())

    # ---- statements -------------------------------------------------

    def statement(self):
        tok = self.peek()
        line = tok.line
        if tok.kind != WORD:
            self.error("sententiam")
        word = tok.value.lower()

        # Prayers
        if self.at("laudetur", "omnissiah") or self.at("unge", "machinam"):
            self.advance(2)
            self.end_statement()
            return Node("praise", line)

        # Spirits and reliquaries
        if self.at("excita", "spiritum") or self.at("excita", "reliquiarium"):
            is_list = self.at("excita", "reliquiarium")
            self.advance(2)
            name = self.name()
            self.end_statement()
            return Node("declare", line, name=name, is_list=is_list)

        if word in ("infunde", "pone"):
            self.advance()
            expr = self.expression()
            self.expect_words("in")
            name = self.name()
            self.end_statement()
            return Node("assign" if word == "infunde" else "append", line, name=name, expr=expr)

        # Ritual arithmetic
        if word in ("benedic", "castiga"):
            self.advance()
            name = self.name()
            self.end_statement()
            return Node("augment", line, name=name, op="plus",
                        expr=Node("literal", line, value=1 if word == "benedic" else -1))

        if word == "adde":
            self.advance()
            expr = self.expression(no_index=True)  # "ad" here means "to", not an index
            self.expect_words("ad")
            name = self.name()
            self.end_statement()
            return Node("augment", line, name=name, op="plus", expr=expr)

        if word == "deme":
            self.advance()
            expr = self.expression()
            self.expect_words("ex")
            name = self.name()
            self.end_statement()
            return Node("augment", line, name=name, op="minus", expr=expr)

        if word in ("multiplica", "divide"):
            self.advance()
            name = self.name()
            self.expect_words("per")
            expr = self.expression()
            self.end_statement()
            return Node("augment", line, name=name, op="mul" if word == "multiplica" else "div", expr=expr)

        # Input and output
        if word in ("proclama", "susurra"):
            self.advance()
            expr = self.expression()
            self.end_statement()
            return Node("print", line, expr=expr, newline=(word == "proclama"))

        if self.at("audi", "vocem"):
            self.advance(2)
            self.expect_words("in")
            name = self.name()
            self.end_statement()
            return Node("input", line, name=name)

        # Flow
        if word == "si":
            return self.if_statement()

        if word == "dum":
            self.advance()
            cond = self.expression()
            self.end_header()
            body = self.loop_body()
            return Node("while", line, cond=cond, body=body)

        if word == "itera":
            self.advance()
            count = self.expression()
            self.expect_words("vicibus")
            self.end_header()
            body = self.loop_body()
            return Node("repeat", line, count=count, body=body)

        if word in ("desine", "perge"):
            if self.loop_depth == 0:
                raise Heresy(f"{tok.value} extra circulum", line)
            self.advance()
            self.end_statement()
            return Node("break" if word == "desine" else "continue", line)

        # Rites
        if word == "ritus":
            return self.rite_definition()

        if word == "redde":
            if self.rite_depth == 0:
                raise Heresy("Redde extra ritum", line)
            self.advance()
            if self.peek().kind == DOT:
                expr = Node("literal", line, value=0)
            else:
                expr = self.expression()
            self.end_statement()
            return Node("return", line, expr=expr)

        if self.at("perage", "ritum"):
            self.advance(2)
            name = self.name()
            args = []
            if self.at("cum"):
                self.advance()
                args = self.arguments()
            self.end_statement()
            return Node("perform", line, call=Node("call", line, name=name, args=args))

        # Heresies
        if word == "tenta":
            self.advance()
            self.end_header()
            body = self.block(lambda: self.at("si", "haeresis", "acciderit") or self.at("amen"))
            handler = []
            if self.at("si", "haeresis", "acciderit"):
                self.advance(3)
                self.end_header()
                handler = self.block(lambda: self.at("amen"))
            self.expect_words("amen")
            self.end_statement()
            return Node("try", line, body=body, handler=handler)

        if self.at("denuntia", "haeresim"):
            self.advance(2)
            expr = self.expression()
            self.end_statement()
            return Node("throw", line, expr=expr)

        if word in ("amen", "aliter"):
            raise Heresy(f"«{tok.value}» sine initio", line)
        if self.at("gloria", "omnissiae"):
            raise Heresy("benedictio intra blocum", line)
        self.error("sententiam")

    def loop_body(self):
        self.loop_depth += 1
        body = self.block(lambda: self.at("amen"))
        self.loop_depth -= 1
        self.expect_words("amen")
        self.end_statement()
        return body

    def if_statement(self):
        line = self.advance().line  # "Si"
        branch_end = lambda: self.at("aliter") or self.at("amen")
        cond = self.expression()
        self.end_header()
        branches = [(cond, self.block(branch_end))]
        else_body = []
        while self.at("aliter"):
            if self.at("aliter", "si"):
                self.advance(2)
                cond = self.expression()
                self.end_header()
                branches.append((cond, self.block(branch_end)))
            else:
                self.advance()
                self.end_header()
                else_body = self.block(lambda: self.at("amen"))
                break
        self.expect_words("amen")
        self.end_statement()
        return Node("if", line, branches=branches, else_body=else_body)

    def rite_definition(self):
        line = self.advance().line  # "Ritus"
        name = self.name()
        params = []
        if self.at("accipiens"):
            self.advance()
            params.append(self.name())
            while self.at("ac"):
                self.advance()
                params.append(self.name())
        if len(set(params)) != len(params):
            raise Heresy(f"ritus {name}: oblationes geminae", line)
        self.end_header()

        saved_loops = self.loop_depth
        self.loop_depth = 0  # Desine cannot escape a rite
        self.rite_depth += 1
        body = self.block(lambda: self.at("amen"))
        self.rite_depth -= 1
        self.loop_depth = saved_loops

        self.expect_words("amen")
        self.end_statement()
        return Node("rite", line, name=name, params=params, body=body)

    # ---- expressions ------------------------------------------------
    #
    #   or       := and ("vel" and)*
    #   and      := not ("et" not)*
    #   not      := "non" not | compare
    #   compare  := arith [comparison-phrase arith]
    #   arith    := term (("plus" | "minus") term)*
    #   term     := unary (("multiplicatum per" | "divisum per" | "residuum") unary)*
    #   unary    := "minus" unary | postfix
    #   postfix  := primary ("ad" unary)*
    #   primary  := verba | numeral | VERUM | FALSUM | NIHIL
    #             | "numerus" postfix (when an operand follows) | NAME ["cum" arg ("ac" arg)*]

    def expression(self, no_index=False):
        saved = self.no_index
        self.no_index = no_index
        try:
            return self.or_expr()
        finally:
            self.no_index = saved

    def or_expr(self):
        left = self.and_expr()
        while self.at("vel"):
            line = self.advance().line
            left = Node("logic", line, op="vel", left=left, right=self.and_expr())
        return left

    def and_expr(self):
        left = self.not_expr()
        while self.at("et"):
            line = self.advance().line
            left = Node("logic", line, op="et", left=left, right=self.not_expr())
        return left

    def not_expr(self):
        if self.at("non"):
            line = self.advance().line
            return Node("not", line, expr=self.not_expr())
        return self.compare_expr()

    _COMPARISONS = (
        (("non", "maior", "quam"), "le"),
        (("non", "minor", "quam"), "ge"),
        (("non", "aequat"), "ne"),
        (("maior", "quam"), "gt"),
        (("minor", "quam"), "lt"),
        (("aequat",), "eq"),
    )

    def compare_expr(self):
        left = self.arith_expr()
        for words, op in self._COMPARISONS:
            if self.at(*words):
                line = self.advance(len(words)).line
                return Node("compare", line, op=op, left=left, right=self.arith_expr())
        return left

    def arith_expr(self):
        left = self.term_expr()
        while self.at("plus") or self.at("minus"):
            tok = self.advance()
            left = Node("binary", tok.line, op=tok.value.lower(), left=left, right=self.term_expr())
        return left

    def term_expr(self):
        left = self.unary_expr()
        while True:
            if self.at("multiplicatum", "per"):
                line, op = self.advance(2).line, "mul"
            elif self.at("divisum", "per"):
                line, op = self.advance(2).line, "div"
            elif self.at("residuum"):
                line, op = self.advance().line, "mod"
            else:
                return left
            left = Node("binary", line, op=op, left=left, right=self.unary_expr())

    def unary_expr(self):
        if self.at("minus"):
            line = self.advance().line
            return Node("negate", line, expr=self.unary_expr())
        return self.postfix_expr()

    def postfix_expr(self):
        expr = self.primary_expr()
        while not self.no_index and self.at("ad"):
            line = self.advance().line
            expr = Node("index", line, target=expr, index=self.unary_expr())
        return expr

    def primary_expr(self):
        tok = self.peek()
        if tok.kind == STRING:
            self.advance()
            return Node("literal", tok.line, value=tok.value)
        if tok.kind == NUMBER:
            if not self.allow_arabic:
                raise Heresy(f"numeri Arabici prohibiti sunt ({tok.value})", tok.line)
            self.advance()
            return Node("literal", tok.line, value=tok.value)
        if tok.kind == WORD:
            word = tok.value.lower()
            if word in ("verum", "falsum", "nihil"):
                self.advance()
                return Node("literal", tok.line, value={"verum": True, "falsum": False, "nihil": 0}[word])
            if word == "numerus" and self.starts_operand(1):
                self.advance()
                return Node("length", tok.line, expr=self.postfix_expr())
            if word not in RESERVED:
                self.advance()
                name = tok.value.upper()
                if self.at("cum"):
                    self.advance()
                    return Node("call", tok.line, name=name, args=self.arguments())
                return Node("name", tok.line, name=name)
        self.error("valorem")

    def starts_operand(self, offset):
        tok = self.peek(offset)
        if tok.kind in (STRING, NUMBER):
            return True
        return tok.kind == WORD and (
            tok.value.lower() not in RESERVED or tok.value.lower() in ("verum", "falsum", "nihil", "minus")
        )

    def arguments(self):
        # Each argument runs to the next "ac" or the end of the expression.
        args = [self.expression()]
        while self.at("ac"):
            self.advance()
            args.append(self.expression())
        return args


# ======================================================================
#  Interpreter
# ======================================================================


class Rite:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class Interpreter:
    PIETY_WARNING = 10
    PIETY_LIMIT = 20
    MAX_RITE_DEPTH = 400

    def __init__(self, stdin=None, stdout=None, stderr=None, incensum=False):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.incensum = incensum
        self.frames = [{}]  # frames[0] holds the global spirits
        self.rites = {}
        self.piety = 0
        self.allow_arabic = False

    @property
    def globals(self):
        return self.frames[0]

    # ---- running ----------------------------------------------------

    def run(self, program):
        self.allow_arabic = program.allow_arabic
        if program.allow_arabic:
            self.warn("Numeri Arabici tolerantur, sed suspecti sunt")
        # Top-level rites are known from the start, so order does not matter.
        for stmt in program.body:
            if stmt.kind == "rite":
                self.rites[stmt.name] = Rite(stmt.name, stmt.params, stmt.body)
        try:
            self.exec_block(program.body)
        except RecursionError:
            raise Heresy("abyssus recursionis") from None
        finally:
            self.stdout.flush()

    def warn(self, message):
        self.stdout.flush()
        print(f"+++ {message} +++", file=self.stderr)

    def tick(self, line):
        """The rule of piety: every executed statement weighs on the spirit."""
        self.piety += 1
        if self.piety == self.PIETY_WARNING:
            self.warn(f"Spiritus machinae inquietus est (linea {to_roman(line)})")
        if self.piety >= self.PIETY_LIMIT:
            self.piety = 0
            raise Heresy("impietas", line)

    def exec_block(self, statements):
        for stmt in statements:
            self.execute(stmt)

    def execute(self, stmt):
        if stmt.kind == "praise":
            self.piety = 0
            return
        self.tick(stmt.line)
        try:
            getattr(self, "exec_" + stmt.kind)(stmt)
        except Heresy as heresy:
            if heresy.line is None:
                heresy.line = stmt.line
            raise

    # ---- spirits ----------------------------------------------------

    def lookup(self, name):
        frame = self.frames[-1]
        if name in frame:
            return frame[name]
        if name in self.globals:
            return self.globals[name]
        raise Heresy(f"spiritus {name} non excitatus est")

    def store(self, name, value):
        frame = self.frames[-1]
        if name in frame:
            frame[name] = value
        elif name in self.globals:
            self.globals[name] = value
        else:
            raise Heresy(f"spiritus {name} non excitatus est")

    # ---- statements -------------------------------------------------

    def exec_declare(self, s):
        self.frames[-1][s.name] = [] if s.is_list else 0

    def exec_assign(self, s):
        self.store(s.name, self.evaluate(s.expr))

    def exec_append(self, s):
        target = self.lookup(s.name)
        if not isinstance(target, list):
            raise Heresy(f"{s.name} non est reliquiarium")
        target.append(self.evaluate(s.expr))

    def exec_augment(self, s):
        current = self.lookup(s.name)
        self.store(s.name, self.binary(s.op, current, self.evaluate(s.expr)))

    def exec_print(self, s):
        text = show(self.evaluate(s.expr))
        if s.newline:
            self.stdout.write(text + "\n")
            if self.incensum:
                self.stdout.write("+++\n")
        else:
            self.stdout.write(text)
            self.stdout.flush()

    def exec_input(self, s):
        self.stdout.flush()
        raw = self.stdin.readline()
        self.store(s.name, self.parse_input(raw))

    def parse_input(self, raw):
        if raw == "":
            return 0  # silence of the void
        text = raw.rstrip("\r\n")
        word = text.strip()
        if word.upper() == "NIHIL":
            return 0
        if looks_roman(word):
            value = from_roman(word)
            if value is not None:
                return value
        if self.allow_arabic and re.fullmatch(r"-?\d+", word):
            return int(word)
        return text

    def exec_if(self, s):
        for cond, body in s.branches:
            if truthy(self.evaluate(cond)):
                self.exec_block(body)
                return
        self.exec_block(s.else_body)

    def exec_while(self, s):
        while truthy(self.evaluate(s.cond)):
            try:
                self.exec_block(s.body)
            except _Continue:
                continue
            except _Break:
                break

    def exec_repeat(self, s):
        count = as_number(self.evaluate(s.count))
        frame = self.frames[-1]
        had_previous = "ITERATIO" in frame
        previous = frame.get("ITERATIO")
        try:
            for i in range(1, count + 1):
                frame["ITERATIO"] = i
                try:
                    self.exec_block(s.body)
                except _Continue:
                    continue
                except _Break:
                    break
        finally:
            if had_previous:
                frame["ITERATIO"] = previous
            else:
                frame.pop("ITERATIO", None)

    def exec_break(self, s):
        raise _Break()

    def exec_continue(self, s):
        raise _Continue()

    def exec_rite(self, s):
        self.rites[s.name] = Rite(s.name, s.params, s.body)

    def exec_return(self, s):
        raise _Return(self.evaluate(s.expr))

    def exec_perform(self, s):
        self.evaluate(s.call)

    def exec_try(self, s):
        try:
            self.exec_block(s.body)
        except Heresy as heresy:
            self.frames[-1]["HAERESIS"] = heresy.message
            self.exec_block(s.handler)

    def exec_throw(self, s):
        raise Heresy(show(self.evaluate(s.expr)))

    # ---- rites ------------------------------------------------------

    def call(self, name, arg_nodes, line):
        rite = self.rites.get(name)
        if rite is None:
            raise Heresy(f"ritus ignotus: {name}")
        if len(arg_nodes) != len(rite.params):
            raise Heresy(
                f"ritus {name} {to_roman(len(rite.params))} oblationes exspectat, "
                f"{to_roman(len(arg_nodes))} accepit"
            )
        values = [self.evaluate(a) for a in arg_nodes]
        self.tick(line)  # each rite performed adds to the piety counter
        if len(self.frames) > self.MAX_RITE_DEPTH:
            raise Heresy("abyssus recursionis")
        self.frames.append(dict(zip(rite.params, values)))
        try:
            self.exec_block(rite.body)
            return 0
        except _Return as ret:
            return ret.value
        finally:
            self.frames.pop()

    # ---- expressions ------------------------------------------------

    def evaluate(self, e):
        kind = e.kind
        if kind == "literal":
            return e.value
        if kind == "name":
            return self.resolve_name(e)
        if kind == "call":
            return self.call(e.name, e.args, e.line)
        if kind == "binary":
            return self.binary(e.op, self.evaluate(e.left), self.evaluate(e.right))
        if kind == "compare":
            return self.compare(e.op, self.evaluate(e.left), self.evaluate(e.right))
        if kind == "logic":
            left = truthy(self.evaluate(e.left))
            if e.op == "et":
                return left and truthy(self.evaluate(e.right))
            return left or truthy(self.evaluate(e.right))
        if kind == "not":
            return not truthy(self.evaluate(e.expr))
        if kind == "negate":
            return -as_number(self.evaluate(e.expr))
        if kind == "index":
            return self.index(self.evaluate(e.target), self.evaluate(e.index))
        if kind == "length":
            value = self.evaluate(e.expr)
            if not isinstance(value, (list, str)):
                raise Heresy("numerus tantum reliquiarum et verborum")
            return len(value)
        raise Heresy(f"nodus ignotus: {kind}")

    def resolve_name(self, e):
        # Spirits shadow numerals, numerals shadow rites.
        name = e.name
        frame = self.frames[-1]
        if name in frame:
            return frame[name]
        if name in self.globals:
            return self.globals[name]
        if looks_roman(name):
            value = from_roman(name)
            if value is None:
                raise Heresy(f"numerus deformis: {name}")
            return value
        if name in self.rites:
            return self.call(name, [], e.line)
        raise Heresy(f"spiritus {name} non excitatus est")

    @staticmethod
    def binary(op, a, b):
        if op == "plus":
            if isinstance(a, str) or isinstance(b, str):
                return show(a) + show(b)
            if isinstance(a, list) and isinstance(b, list):
                return a + b
            return as_number(a) + as_number(b)
        a, b = as_number(a), as_number(b)
        if op == "minus":
            return a - b
        if op == "mul":
            return a * b
        if op == "div":
            return trunc_div(a, b)
        if op == "mod":
            return trunc_mod(a, b)
        raise Heresy(f"operatio ignota: {op}")

    @staticmethod
    def compare(op, a, b):
        if op == "eq":
            return values_equal(a, b)
        if op == "ne":
            return not values_equal(a, b)
        if not (isinstance(a, str) and isinstance(b, str)):
            a, b = as_number(a), as_number(b)
        return {"gt": a > b, "lt": a < b, "ge": a >= b, "le": a <= b}[op]

    @staticmethod
    def index(target, position):
        if not isinstance(target, (list, str)):
            raise Heresy("index tantum in reliquiario")
        position = as_number(position)
        if position < 1 or position > len(target):
            raise Heresy("reliquia ad nihilum non existit")
        return target[position - 1]


# ======================================================================
#  Entry point
# ======================================================================


def run_source(source, stdin=None, stdout=None, stderr=None, incensum=False):
    """Parse and run a litany. Returns the process exit code."""
    stderr = stderr or sys.stderr
    stdout = stdout or sys.stdout
    try:
        program = Parser(lex(source)).parse()
    except Heresy as heresy:
        print(f"+++ HAERESIS +++ {heresy}", file=stderr)
        return 666

    interpreter = Interpreter(stdin, stdout, stderr, incensum)
    try:
        interpreter.run(program)
    except Heresy as heresy:
        stdout.flush()
        print(f"+++ HAERESIS +++ {heresy}", file=stderr)
        return 666

    if not program.blessed:
        print("+++ Spiritus machinae non placatus est +++", file=stderr)
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="litania",
        description="Run a LITANIA program. In nomine Omnissiae.",
    )
    parser.add_argument("file", help="the .lit litany to perform")
    parser.add_argument("--incensum", action="store_true",
                        help="print +++ after every proclaimed line, for ceremonial use")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    try:
        with open(args.file, encoding="utf-8") as handle:
            source = handle.read()
    except OSError as err:
        print(f"+++ HAERESIS +++ codex legi non potest: {err}", file=sys.stderr)
        return 666

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    return run_source(source, incensum=args.incensum)


if __name__ == "__main__":
    sys.exit(main())
