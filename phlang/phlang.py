# Danger: Confusion and multiple possible headaches ahead.

USEGUI = False # Don't turn this on in a headless environment. It's off by default because it breaks things when it's on.

import os
import string
import time
import math
from importlib import import_module
if USEGUI:
  import tkinter as tk
import sys
import urllib.request

execGlobals = {}
execLocals = {}

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

# Gui Globals
WINDOW = None

def createWindow(title, background):
  if USEGUI:
    global WINDOW
    WINDOW = tk.Tk()
    WINDOW.title(title)
    WINDOW.geometry("600x400")
    WINDOW.resizable(0, 0)
    WINDOW.protocol("WM_DELETE_WINDOW", sys.exit)
    WINDOW.configure(background=background)

def closeWindow():
  if USEGUI:
    WINDOW.destroy()

def getWindowWidth():
  if USEGUI:
    return WINDOW.winfo_width()

def getWindowHeight():
  if USEGUI:
    return WINDOW.winfo_height()

def resizeWindow(height, width):
  if USEGUI:
    WINDOW.geometry(f"{width}x{height}")

def clearWindow():
  if USEGUI:
    WINDOW.delete('all')

def addButton(text, x, y, pyfunc):
  if USEGUI:
    button = tk.Button(WINDOW, text=text, command=lambda: run("<onClick>", pyfunc))
    button.place(x=x, y=y)

def addText(text, x, y):
  if USEGUI:
    text = tk.Label(WINDOW, text=text)
    text.place(x=x,y=y)

def hang():
  while True:
    pass

def string_with_arrows(text, pos_start, pos_end):
  result = ''

  # Calculate indices
  idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
  idx_end = text.find('\n', idx_start + 1)
  if idx_end < 0: idx_end = len(text)
  
  # Generate each line
  line_count = pos_end.ln - pos_start.ln + 1
  for i in range(line_count):
    # Calculate line columns
    line = text[idx_start:idx_end]
    col_start = pos_start.col if i == 0 else 0
    col_end = pos_end.col if i == line_count - 1 else len(line) - 1

    # Append to result
    result += line + '\n'
    result += ' ' * col_start + '^' * (col_end - col_start)

    # Re-calculate indices
    idx_start = idx_end
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)

  return result.replace('\t', '')

class Error:
  def __init__(self, pos_start, pos_end, error_name, details):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details

  def as_string(self):
    result  = f'{self.error_name}: {self.details}\n'
    result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

class IllegalCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, pos_start, pos_end, details=''):
    super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
  def __init__(self, pos_start, pos_end, details, context):
    super().__init__(pos_start, pos_end, 'Runtime Error', details)
    self.context = context

  def as_string(self):
    result  = self.generate_traceback()
    result += f'{self.error_name}: {self.details}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

  def generate_traceback(self):
    result = ''
    pos = self.pos_start
    ctx = self.context

    while ctx:
      result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
      pos = ctx.parent_entry_pos
      ctx = ctx.parent

    return 'Traceback (most recent call):\n' + result

class Position:
  def __init__(self, idx, ln, col, fn, ftxt):
    self.idx = idx
    self.ln = ln
    self.col = col
    self.fn = fn
    self.ftxt = ftxt

  def advance(self, current_char=None):
    self.idx += 1
    self.col += 1

    if current_char == '\n':
      self.ln += 1
      self.col = 0

    return self

  def copy(self):
    return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

TT_INT        = 'int'
TT_FLOAT      = 'float'
TT_STRING      = 'string'
TT_IDENTIFIER  = 'identifier'
TT_KEYWORD    = 'keyword'
TT_PLUS       = 'plus'
TT_MINUS      = 'minus'
TT_MUL        = 'mul'
TT_DIV        = 'div'
TT_POW        = 'pow'
TT_EQ          = 'eq'
TT_LPAREN     = 'lparen'
TT_RPAREN     = 'rparen'
TT_LSQUARE    = 'lsquare'
TT_RSQUARE    = 'rsquare'
TT_EE          = 'ee'
TT_NE          = 'ne'
TT_LT          = 'lt'
TT_GT          = 'gt'
TT_LTE        = 'lte'
TT_GTE        = 'gte'
TT_COMMA      = 'comma'
TT_ARROW      = 'arrow'
TT_NEWLINE    = 'newline'
TT_EOF        = 'eof'

KEYWORDS = [
  'var',
  'and',
  'or',
  'not',
  'if',
  'elif',
  'else',
  'for',
  'to',
  'step',
  'while',
  'func',
  'then',
  'end',
  'return',
  'continue',
  'break',
]

class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value

    if pos_start:
      self.pos_start = pos_start.copy()
      self.pos_end = pos_start.copy()
      self.pos_end.advance()

    if pos_end:
      self.pos_end = pos_end.copy()

  def matches(self, type_, value):
    return self.type == type_ and self.value == value

  def __repr__(self):
    if self.value: return f'{self.type}:{self.value}'
    return f'{self.type}'

class Lexer:
  def __init__(self, fn, text):
    self.fn = fn
    self.text = text
    self.pos = Position(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()

  def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

  def make_tokens(self):
    tokens = []

    while self.current_char != None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char == '#':
        self.skip_comment()
      elif self.current_char in ';\n':
        tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
        self.advance()
      elif self.current_char in DIGITS:
        tokens.append(self.make_number())
      elif self.current_char in LETTERS:
        tokens.append(self.make_identifier())
      elif self.current_char == '"':
        tokens.append(self.make_string())
      elif self.current_char == '+':
        tokens.append(Token(TT_PLUS, pos_start=self.pos))
        self.advance()
      elif self.current_char == '-':
        tokens.append(self.make_minus_or_arrow())
      elif self.current_char == '*':
        tokens.append(Token(TT_MUL, pos_start=self.pos))
        self.advance()
      elif self.current_char == '/':
        tokens.append(Token(TT_DIV, pos_start=self.pos))
        self.advance()
      elif self.current_char == '^':
        tokens.append(Token(TT_POW, pos_start=self.pos))
        self.advance()
      elif self.current_char == '(':
        tokens.append(Token(TT_LPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == ')':
        tokens.append(Token(TT_RPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '[':
        tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == ']':
        tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '!':
        token, error = self.make_not_equals()
        if error: return [], error
        tokens.append(token)
      elif self.current_char == '=':
        tokens.append(self.make_equals())
      elif self.current_char == '<':
        tokens.append(self.make_less_than())
      elif self.current_char == '>':
        tokens.append(self.make_greater_than())
      elif self.current_char == ',':
        tokens.append(Token(TT_COMMA, pos_start=self.pos))
        self.advance()
      else:
        pos_start = self.pos.copy()
        char = self.current_char
        self.advance()
        return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    tokens.append(Token(TT_EOF, pos_start=self.pos))
    return tokens, None

  def make_number(self):
    num_str = ''
    dot_count = 0
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in DIGITS + '.':
      if self.current_char == '.':
        if dot_count == 1: break
        dot_count += 1
      num_str += self.current_char
      self.advance()

    if dot_count == 0:
      return Token(TT_INT, int(num_str), pos_start, self.pos)
    else:
      return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

  def make_string(self):
    string = ''
    pos_start = self.pos.copy()
    escape_character = False
    self.advance()

    escape_characters = {
      'n': '\n',
      't': '\t',
      '"': '"'
    }

    while self.current_char != None and (self.current_char != '"' or escape_character):
      if escape_character:
        string += escape_characters.get(self.current_char, self.current_char)
      else:
        if self.current_char == '\\':
          escape_character = True
          self.advance()
          continue
        else:
          string += self.current_char
      self.advance()
      escape_character = False

    self.advance()
    return Token(TT_STRING, string, pos_start, self.pos)

  def make_identifier(self):
    id_str = ''
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
      id_str += self.current_char
      self.advance()

    tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
    return Token(tok_type, id_str, pos_start, self.pos)

  def make_minus_or_arrow(self):
    tok_type = TT_MINUS
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '>':
      self.advance()
      tok_type = TT_ARROW

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_not_equals(self):
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

    self.advance()
    return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

  def make_equals(self):
    tok_type = TT_EQ
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_EE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_less_than(self):
    tok_type = TT_LT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_LTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_greater_than(self):
    tok_type = TT_GT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_GTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def skip_comment(self):
    self.advance()

    while self.current_char != '\n':
      self.advance()

    self.advance()



class NumberNode:
  def __init__(self, tok):
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class StringNode:
  def __init__(self, tok):
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class ListNode:
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes

    self.pos_start = pos_start
    self.pos_end = pos_end

class VarAccessNode:
  def __init__(self, var_name_tok):
    self.var_name_tok = var_name_tok

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
  def __init__(self, var_name_tok, value_node):
    self.var_name_tok = var_name_tok
    self.value_node = value_node

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end

class BinOpNode:
  def __init__(self, left_node, op_tok, right_node):
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node

    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

  def __repr__(self):
    return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
  def __init__(self, op_tok, node):
    self.op_tok = op_tok
    self.node = node

    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end

  def __repr__(self):
    return f'({self.op_tok}, {self.node})'

class IfNode:
  def __init__(self, cases, else_case):
    self.cases = cases
    self.else_case = else_case

    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

class ForNode:
  def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
    self.var_name_tok = var_name_tok
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.step_value_node = step_value_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.body_node.pos_end

class WhileNode:
  def __init__(self, condition_node, body_node, should_return_null):
    self.condition_node = condition_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end

class FuncDefNode:
  def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
    self.var_name_tok = var_name_tok
    self.arg_name_toks = arg_name_toks
    self.body_node = body_node
    self.should_auto_return = should_auto_return

    if self.var_name_tok:
      self.pos_start = self.var_name_tok.pos_start
    elif len(self.arg_name_toks) > 0:
      self.pos_start = self.arg_name_toks[0].pos_start
    else:
      self.pos_start = self.body_node.pos_start

    self.pos_end = self.body_node.pos_end

class CallNode:
  def __init__(self, node_to_call, arg_nodes):
    self.node_to_call = node_to_call
    self.arg_nodes = arg_nodes

    self.pos_start = self.node_to_call.pos_start

    if len(self.arg_nodes) > 0:
      self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
    else:
      self.pos_end = self.node_to_call.pos_end

class ReturnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return

    self.pos_start = pos_start
    self.pos_end = pos_end

class ContinueNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end

class BreakNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end


class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0

  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  def success(self, node):
    self.node = node
    return self

  def failure(self, error):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self


class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()

  def advance(self):
    self.tok_idx += 1
    self.update_current_tok()
    return self.current_tok

  def reverse(self, amount=1):
    self.tok_idx -= amount
    self.update_current_tok()
    return self.current_tok

  def update_current_tok(self):
    if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]

  def parse(self):
    res = self.statements()
    if not res.error and self.current_tok.type != TT_EOF:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Token cannot appear after previous tokens"
      ))
    return res


  def statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_tok.pos_start.copy()

    while self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    while True:
      newline_count = 0
      while self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()
        newline_count += 1
      if newline_count == 0:
        more_statements = False

      if not more_statements: break
      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue
      statements.append(statement)

    return res.success(ListNode(
      statements,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def statement(self):
    res = ParseResult()
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.matches(TT_KEYWORD, 'return'):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

    if self.current_tok.matches(TT_KEYWORD, 'continue'):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

    if self.current_tok.matches(TT_KEYWORD, 'break'):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'return', 'continue', 'break', 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
      ))
    return res.success(expr)

  def expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'var'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected identifier"
        ))

      var_name = self.current_tok
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_EQ:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected '='"
        ))

      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      return res.success(VarAssignNode(var_name, expr))

    node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
      ))

    return res.success(node)

  def comp_expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'not'):
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error: return res
      return res.success(UnaryOpNode(op_tok, node))

    node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'func' or 'NOT'"
      ))

    return res.success(node)

  def arith_expr(self):
    return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

  def term(self):
    return self.bin_op(self.factor, (TT_MUL, TT_DIV))

  def factor(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_PLUS, TT_MINUS):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  def power(self):
    return self.bin_op(self.call, (TT_POW, ), self.factor)

  def call(self):
    res = ParseResult()
    atom = res.register(self.atom())
    if res.error: return res

    if self.current_tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      arg_nodes = []

      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
      else:
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ')', 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'not'"
          ))

        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          arg_nodes.append(res.register(self.expr()))
          if res.error: return res

        if self.current_tok.type != TT_RPAREN:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ')'"
          ))

        res.register_advancement()
        self.advance()
      return res.success(CallNode(atom, arg_nodes))
    return res.success(atom)

  def atom(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_INT, TT_FLOAT):
      res.register_advancement()
      self.advance()
      return res.success(NumberNode(tok))

    elif tok.type == TT_STRING:
      res.register_advancement()
      self.advance()
      return res.success(StringNode(tok))

    elif tok.type == TT_IDENTIFIER:
      res.register_advancement()
      self.advance()
      return res.success(VarAccessNode(tok))

    elif tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
        return res.success(expr)
      else:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ')'"
        ))

    elif tok.type == TT_LSQUARE:
      list_expr = res.register(self.list_expr())
      if res.error: return res
      return res.success(list_expr)

    elif tok.matches(TT_KEYWORD, 'if'):
      if_expr = res.register(self.if_expr())
      if res.error: return res
      return res.success(if_expr)

    elif tok.matches(TT_KEYWORD, 'for'):
      for_expr = res.register(self.for_expr())
      if res.error: return res
      return res.success(for_expr)

    elif tok.matches(TT_KEYWORD, 'while'):
      while_expr = res.register(self.while_expr())
      if res.error: return res
      return res.success(while_expr)

    elif tok.matches(TT_KEYWORD, 'func'):
      func_def = res.register(self.func_def())
      if res.error: return res
      return res.success(func_def)

    return res.failure(InvalidSyntaxError(
      tok.pos_start, tok.pos_end,
      "Expected int, float, identifier, '+', '-', '(', '[', if', 'for', 'while', 'fun'"
    ))

  def list_expr(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_RSQUARE:
      res.register_advancement()
      self.advance()
    else:
      element_nodes.append(res.register(self.expr()))
      if res.error:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ']', 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[' or 'not'"
        ))

      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

      if self.current_tok.type != TT_RSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ']'"
        ))

      res.register_advancement()
      self.advance()

    return res.success(ListNode(
      element_nodes,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def if_expr(self):
    res = ParseResult()
    all_cases = res.register(self.if_expr_cases('if'))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  def if_expr_b(self):
    return self.if_expr_cases('elif')

  def if_expr_c(self):
    res = ParseResult()
    else_case = None

    if self.current_tok.matches(TT_KEYWORD, 'else'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        if self.current_tok.matches(TT_KEYWORD, 'end'):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'end'"
          ))
      else:
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  def if_expr_b_or_c(self):
    res = ParseResult()
    cases, else_case = [], None

    if self.current_tok.matches(TT_KEYWORD, 'elif'):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else:
      else_case = res.register(self.if_expr_c())
      if res.error: return res

    return res.success((cases, else_case))

  def if_expr_cases(self, case_keyword):
    res = ParseResult()
    cases = []
    else_case = None

    if not self.current_tok.matches(TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '{case_keyword}'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      if self.current_tok.matches(TT_KEYWORD, 'end'):
        res.register_advancement()
        self.advance()
      else:
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else:
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)

    return res.success((cases, else_case))

  def for_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'for'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'for'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected identifier"
      ))

    var_name = self.current_tok
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_EQ:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '='"
      ))

    res.register_advancement()
    self.advance()

    start_value = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'to'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'TO'"
      ))

    res.register_advancement()
    self.advance()

    end_value = res.register(self.expr())
    if res.error: return res

    if self.current_tok.matches(TT_KEYWORD, 'step'):
      res.register_advancement()
      self.advance()

      step_value = res.register(self.expr())
      if res.error: return res
    else:
      step_value = None

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'end'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'end'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

  def while_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'while'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'while'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'end'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'end'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))

  def func_def(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'func'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'func'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_IDENTIFIER:
      var_name_tok = self.current_tok
      res.register_advancement()
      self.advance()
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '('"
        ))
    else:
      var_name_tok = None
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or '('"
        ))

    res.register_advancement()
    self.advance()
    arg_name_toks = []

    if self.current_tok.type == TT_IDENTIFIER:
      arg_name_toks.append(self.current_tok)
      res.register_advancement()
      self.advance()

      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier"
          ))

        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()

      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ')'"
        ))
    else:
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or ')'"
        ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_ARROW:
      res.register_advancement()
      self.advance()

      body = res.register(self.expr())
      if res.error: return res

      return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        True
      ))

    if self.current_tok.type != TT_NEWLINE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '->' or NEWLINE"
      ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'end'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'end'"
      ))

    res.register_advancement()
    self.advance()

    return res.success(FuncDefNode(
      var_name_tok,
      arg_name_toks,
      body,
      False
    ))


  def bin_op(self, func_a, ops, func_b=None):
    if func_b == None:
      func_b = func_a

    res = ParseResult()
    left = res.register(func_a())
    if res.error: return res

    while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()
      right = res.register(func_b())
      if res.error: return res
      left = BinOpNode(left, op_tok, right)

    return res.success(left)



class RTResult:
  def __init__(self):
    self.reset()

  def reset(self):
    self.value = None
    self.error = None
    self.func_return_value = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def register(self, res):
    self.error = res.error
    self.func_return_value = res.func_return_value
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  def success(self, value):
    self.reset()
    self.value = value
    return self

  def success_return(self, value):
    self.reset()
    self.func_return_value = value
    return self

  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  def failure(self, error):
    self.reset()
    self.error = error
    return self

  def should_return(self):
    return (
      self.error or
      self.func_return_value or
      self.loop_should_continue or
      self.loop_should_break
    )



class Value:
  def __init__(self):
    self.set_pos()
    self.set_context()

  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context=None):
    self.context = context
    return self

  def added_to(self, other):
    return None, self.illegal_operation(other)

  def subbed_by(self, other):
    return None, self.illegal_operation(other)

  def multed_by(self, other):
    return None, self.illegal_operation(other)

  def dived_by(self, other):
    return None, self.illegal_operation(other)

  def powed_by(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_eq(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_ne(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lte(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gte(self, other):
    return None, self.illegal_operation(other)

  def anded_by(self, other):
    return None, self.illegal_operation(other)

  def ored_by(self, other):
    return None, self.illegal_operation(other)

  def notted(self, other):
    return None, self.illegal_operation(other)

  def execute(self, args):
    return RTResult().failure(self.illegal_operation())

  def copy(self):
    raise Exception('No copy method defined')

  def is_true(self):
    return False

  def illegal_operation(self, other=None):
    if not other: other = self
    return RTError(
      self.pos_start, other.pos_end,
      'Illegal operation',
      self.context
    )

class Number(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def subbed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Number(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def powed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def anded_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def ored_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None

  def copy(self):
    copy = Number(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def is_true(self):
    return self.value != 0

  def __str__(self):
    return str(self.value)

  def __repr__(self):
    return str(self.value)

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)
Number.e = Number(math.e)
Number.inf = Number(math.inf)
Number.nan = Number(math.nan)
Number.tau = Number(math.tau)

class String(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return String(self.value[other.value]).set_context(self.context), None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from string because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, String):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, String):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def is_true(self):
    return len(self.value) > 0

  def copy(self):
    copy = String(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return self.value

  def __repr__(self):
    return f'"{self.value}"'

class List(Value):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

  def added_to(self, other):
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None

  def subbed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be removed from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  def copy(self):
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return ", ".join([str(x) for x in self.elements])

  def __repr__(self):
    return f'[{", ".join([repr(x) for x in self.elements])}]'

class BaseFunction(Value):
  def __init__(self, name):
    super().__init__()
    self.name = name or "<anonymous>"

  def generate_new_context(self):
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
    return new_context

  def check_args(self, arg_names, args):
    res = RTResult()

    if len(args) > len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(args) - len(arg_names)} too many args passed into {self}",
        self.context
      ))

    if len(args) < len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(arg_names) - len(args)} too few args passed into {self}",
        self.context
      ))

    return res.success(None)

  def populate_args(self, arg_names, args, exec_ctx):
    for i in range(len(args)):
      arg_name = arg_names[i]
      arg_value = args[i]
      arg_value.set_context(exec_ctx)
      exec_ctx.symbol_table.set(arg_name, arg_value)

  def check_and_populate_args(self, arg_names, args, exec_ctx):
    res = RTResult()
    res.register(self.check_args(arg_names, args))
    if res.should_return(): return res
    self.populate_args(arg_names, args, exec_ctx)
    return res.success(None)

class Function(BaseFunction):
  def __init__(self, name, body_node, arg_names, should_auto_return):
    super().__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_auto_return = should_auto_return

  def execute(self, args):
    res = RTResult()
    interpreter = Interpreter()
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_return_value == None: return res

    ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
    return res.success(ret_value)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = RTResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)

  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"


  def execute_print(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return RTResult().success(Number.null)
  execute_print.arg_names = ['value']

  def execute_python(self, exec_ctx):
    code = exec_ctx.symbol_table.get('value')
    try:
      result = compile(code.value.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r'), "<eval>", "exec")
      result = exec(result, execGlobals, execLocals)
      text = str(result)
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f'Python error: {str(e)}',
        exec_ctx
      ))
    return RTResult().success(String(text))
  execute_python.arg_names = ['value']



  def execute_print_ret(self, exec_ctx):
    return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
  execute_print_ret.arg_names = ['value']

  def execute_input(self, exec_ctx):
    text = input()
    return RTResult().success(String(text))
  execute_input.arg_names = []

  def execute_read_file(self, exec_ctx):
    file_name = exec_ctx.symbol_table.get('value')
    try:
      with open(file_name.value) as f:
        text = f.read()
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f'Failed to open file {file_name.value}',
        exec_ctx
      ))
    return RTResult().success(String(text))
  execute_read_file.arg_names = ['value']

  def execute_input_int(self, exec_ctx):
    while True:
      text = input()
      try:
        number = int(text)
        break
      except ValueError:
        print(f"'{text}' must be an integer. Try again!")
    return RTResult().success(Number(number))
  execute_input_int.arg_names = []

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'cls')
    return RTResult().success(Number.null)
  execute_clear.arg_names = []

  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_python_import(self, exec_ctx):
    code = exec_ctx.symbol_table.get('value')
    try:
      globals()[code.value] = import_module(code.value)
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f'Python error: {str(e)}',
        exec_ctx
      ))
    return RTResult().success(Number.null)
  execute_python_import.arg_names = ['value']

  def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_function.arg_names = ["value"]

  def execute_append(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    value = exec_ctx.symbol_table.get("value")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    list_.elements.append(value)
    return RTResult().success(Number.null)
  execute_append.arg_names = ["list", "value"]

  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be number",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RTResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_table.get("listA")
    listB = exec_ctx.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RTResult().success(Number.null)
  execute_extend.arg_names = ["listA", "listB"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List) and not isinstance(list_, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be list or string",
        exec_ctx
      ))

    if isinstance(list_, List):
      return RTResult().success(Number(len(list_.elements)))

    return RTResult().success(Number(len(list_.value)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be string",
        exec_ctx
      ))

    fn = fn.value

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:

      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)

    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))

    return RTResult().success(Number.null)
  execute_run.arg_names = ["fn"]

  def execute_open_window(self, exec_ctx):
    createWindow(str(exec_ctx.symbol_table.get("title")), str(exec_ctx.symbol_table.get("background")))
    return RTResult().success(Number.null)
  execute_open_window.arg_names = ["title", "background"]

  def execute_close_window(self, exec_ctx):
    closeWindow()
    return RTResult().success(Number.null)
  execute_close_window.arg_names = []

  def execute_window_width(self, exec_ctx):
    return RTResult().success(Number(getWindowWidth()))
  execute_window_width.arg_names = []

  def execute_window_height(self, exec_ctx):
    return RTResult().success(Number(getWindowHeight()))
  execute_window_height.arg_names = []
  
  def execute_resize_window(self, exec_ctx):
    resizeWindow(exec_ctx.symbol_table.get("width").value, exec_ctx.symbol_table.get("height").value)
    return RTResult().success(Number.null)
  execute_resize_window.arg_names = ["height", "width"]

  def execute_clear_window(self, exec_ctx):
    clearWindow()
    return RTResult().success(Number.null)
  execute_clear_window.arg_names = []

  def execute_create_button(self, exec_ctx):
    addButton(str(exec_ctx.symbol_table.get("text")), exec_ctx.symbol_table.get("x").value, exec_ctx.symbol_table.get("y").value, exec_ctx.symbol_table.get("functionname").value)
    return RTResult().success(Number.null)
  execute_create_button.arg_names = ["text", "x", "y", "functionname"]

  def execute_create_text(self, exec_ctx):
    addText(str(exec_ctx.symbol_table.get("text")), exec_ctx.symbol_table.get("x").value, exec_ctx.symbol_table.get("y").value)
    return RTResult().success(Number.null)
  execute_create_text.arg_names = ["text", "x", "y"]

  def execute_math_acos(self, exec_ctx):
    return RTResult().success(Number(math.acos(exec_ctx.symbol_table.get("x").value)))
  execute_math_acos.arg_names = ["x"]

  def execute_math_acosh(self, exec_ctx):
    return RTResult().success(Number(math.acosh(exec_ctx.symbol_table.get("x").value)))
  execute_math_acosh.arg_names = ["x"]

  def execute_math_asin(self, exec_ctx):
    return RTResult().success(Number(math.asin(exec_ctx.symbol_table.get("x").value)))
  execute_math_asin.arg_names = ["x"]

  def execute_math_asinh(self, exec_ctx):
    return RTResult().success(Number(math.asinh(exec_ctx.symbol_table.get("x").value)))
  execute_math_asinh.arg_names = ["x"]

  def execute_math_atan(self, exec_ctx):
    return RTResult().success(Number(math.atan(exec_ctx.symbol_table.get("x").value)))
  execute_math_atan.arg_names = ["x"]

  def execute_math_atanh(self, exec_ctx):
    return RTResult().success(Number(math.atanh(exec_ctx.symbol_table.get("x").value)))
  execute_math_atanh.arg_names = ["x"]

  def execute_math_atan2(self, exec_ctx):
    return RTResult().success(Number(math.atan2(exec_ctx.symbol_table.get("y").value, exec_ctx.symbol_table.get("x").value)))
  execute_math_atan2.arg_names = ["y", "x"]

  def execute_math_cbrt(self, exec_ctx):
    return RTResult().success(Number(math.cbrt(exec_ctx.symbol_table.get("x").value)))
  execute_math_cbrt.arg_names = ["x"]

  def execute_math_ceil(self, exec_ctx):
    return RTResult().success(Number(math.ceil(exec_ctx.symbol_table.get("x").value)))
  execute_math_ceil.arg_names = ["x"]

  def execute_math_cos(self, exec_ctx):
    return RTResult().success(Number(math.cos(exec_ctx.symbol_table.get("x").value)))
  execute_math_cos.arg_names = ["x"]

  def execute_math_cosh(self, exec_ctx):
    return RTResult().success(Number(math.cosh(exec_ctx.symbol_table.get("x").value)))
  execute_math_cosh.arg_names = ["x"]

  def execute_math_degrees(self, exec_ctx):
    return RTResult().success(Number(math.degrees(exec_ctx.symbol_table.get("x").value)))
  execute_math_degrees.arg_names = ["x"]

  def execute_math_erf(self, exec_ctx):
    return RTResult().success(Number(math.erf(exec_ctx.symbol_table.get("x").value)))
  execute_math_erf.arg_names = ["x"]

  def execute_math_erfc(self, exec_ctx):
    return RTResult().success(Number(math.erfc(exec_ctx.symbol_table.get("x").value)))
  execute_math_erfc.arg_names = ["x"]

  def execute_math_exp(self, exec_ctx):
    return RTResult().success(Number(math.exp(exec_ctx.symbol_table.get("x").value)))
  execute_math_exp.arg_names = ["x"]

  def execute_math_expm1(self, exec_ctx):
    return RTResult().success(Number(math.expm1(exec_ctx.symbol_table.get("x").value)))
  execute_math_expm1.arg_names = ["x"]

  def execute_math_floor(self, exec_ctx):
    return RTResult().success(Number(math.floor(exec_ctx.symbol_table.get("x").value)))
  execute_math_floor.arg_names = ["x"]

  def execute_math_gamma(self, exec_ctx):
    return RTResult().success(Number(math.gamma(exec_ctx.symbol_table.get("x").value)))
  execute_math_gamma.arg_names = ["x"]

  def execute_math_lgamma(self, exec_ctx):
    return RTResult().success(Number(math.lgamma(exec_ctx.symbol_table.get("x").value)))
  execute_math_lgamma.arg_names = ["x"]

  def execute_math_log(self, exec_ctx):
    return RTResult().success(Number(math.log(exec_ctx.symbol_table.get("x").value)))
  execute_math_log.arg_names = ["x"]

  def execute_math_log10(self, exec_ctx):
    return RTResult().success(Number(math.log10(exec_ctx.symbol_table.get("x").value)))
  execute_math_log10.arg_names = ["x"]

  def execute_math_log1p(self, exec_ctx):
    return RTResult().success(Number(math.log1p(exec_ctx.symbol_table.get("x").value)))
  execute_math_log1p.arg_names = ["x"]

  def execute_math_log2(self, exec_ctx):
    return RTResult().success(Number(math.log2(exec_ctx.symbol_table.get("x").value)))
  execute_math_log2.arg_names = ["x"]

  def execute_math_radians(self, exec_ctx):
    return RTResult().success(Number(math.radians(exec_ctx.symbol_table.get("x").value)))
  execute_math_radians.arg_names = ["x"]

  def execute_math_sin(self, exec_ctx):
    return RTResult().success(Number(math.sin(exec_ctx.symbol_table.get("x").value)))
  execute_math_sin.arg_names = ["x"]

  def execute_math_sinh(self, exec_ctx):
    return RTResult().success(Number(math.sinh(exec_ctx.symbol_table.get("x").value)))
  execute_math_sinh.arg_names = ["x"]

  def execute_math_sqrt(self, exec_ctx):
    return RTResult().success(Number(math.sqrt(exec_ctx.symbol_table.get("x").value)))
  execute_math_sqrt.arg_names = ["x"]

  def execute_math_tan(self, exec_ctx):
    return RTResult().success(Number(math.tan(exec_ctx.symbol_table.get("x").value)))
  execute_math_tan.arg_names = ["x"]

  def execute_math_tanh(self, exec_ctx):
    return RTResult().success(Number(math.tanh(exec_ctx.symbol_table.get("x").value)))
  execute_math_tanh.arg_names = ["x"]

  def execute_math_trunc(self, exec_ctx):
    return RTResult().success(Number(math.trunc(exec_ctx.symbol_table.get("x").value)))
  execute_math_trunc.arg_names = ["x"]
  
  def execute_str_len(self, exec_ctx):
    return RTResult().success(Number(len(exec_ctx.symbol_table.get("x").value)))
  execute_str_len.arg_names = ["x"]

  def execute_str_upper(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.upper()))
  execute_str_upper.arg_names = ["x"]

  def execute_str_lower(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.lower()))
  execute_str_lower.arg_names = ["x"]

  def execute_str_strip(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.strip()))
  execute_str_strip.arg_names = ["x"]

  def execute_str_lstrip(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.lstrip()))
  execute_str_lstrip.arg_names = ["x"]

  def execute_str_rstrip(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.rstrip()))
  execute_str_rstrip.arg_names = ["x"]

  def execute_str_join(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.join(exec_ctx.symbol_table.get("y").value)))
  execute_str_join.arg_names = ["x", "y"]

  def execute_str_split(self, exec_ctx):
    return RTResult().success(List([String(s) for s in exec_ctx.symbol_table.get("x").value.split(exec_ctx.symbol_table.get("y").value)]))
  execute_str_split.arg_names = ["x", "y"]

  def execute_str_replace(self, exec_ctx):
    return RTResult().success(String(exec_ctx.symbol_table.get("x").value.replace(exec_ctx.symbol_table.get("y").value, exec_ctx.symbol_table.get("z").value)))
  execute_str_replace.arg_names = ["x", "y", "z"]

  def execute_str_startswith(self, exec_ctx):
    return RTResult().success(Number( int(exec_ctx.symbol_table.get("x").value.startswith(exec_ctx.symbol_table.get("y").value)) == True))
  execute_str_startswith.arg_names = ["x", "y"]

  def execute_str_endswith(self, exec_ctx):
    return RTResult().success(Number(int(exec_ctx.symbol_table.get("x").value.endswith(exec_ctx.symbol_table.get("y").value == True))))
  execute_str_endswith.arg_names = ["x", "y"]

  def execute_writefile(self, exec_ctx):
    file_name = exec_ctx.symbol_table.get("file_name").value
    content = exec_ctx.symbol_table.get("content").value
    with open(file_name, "w") as f:
      f.write(content)
      f.close()
    return RTResult().success(Number(1))
  execute_writefile.arg_names = ["file_name", "content"]

  def execute_hang(self, exec_ctx):
    hang()
  execute_hang.arg_names = []

  def execute_exit(self, exec_ctx):
    sys.exit(0)
  execute_exit.arg_names = []

  def execute_import(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be string",
        exec_ctx
      ))

    fn = fn.value
    pth = os.path.dirname(__file__)
    pth = os.path.join(pth, 'packages')
    try:
      with open(os.path.join(pth,fn,fn+".ph"), "r") as f:
        script = f.read()
    except Exception as e:

      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    try:
      with open(os.path.join(pth,fn,"init.py"), "r") as f:
        script2 = f.read()
    except Exception as e:

      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"init.py\"\n" + str(e),
        exec_ctx
      ))
    exec(compile(script2, "<init.py> for module " + fn, "exec"), execGlobals, execLocals)

    _, error = run(fn, script)

    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))
    

    return RTResult().success(Number.null)
  execute_import.arg_names = ["fn"]

  def execute_eval(self, exec_ctx):
    result, error = run(exec_ctx.symbol_table.get("fn"))
    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Script threw error whilst executing:\n" +
        error.as_string(),
        exec_ctx
      ))
    return RTResult().success(Number.null)
  execute_eval.arg_names = ["fn"]

  def execute_delay(self, exec_ctx):
    time.sleep(exec_ctx.symbol_table.get("time").value)
    return RTResult().success(Number.null)
  execute_delay.arg_names = ["time"]
  


BuiltInFunction.print         = BuiltInFunction("print")
BuiltInFunction.print_ret     = BuiltInFunction("print_ret")
BuiltInFunction.input         = BuiltInFunction("input")
BuiltInFunction.input_int     = BuiltInFunction("input_int")
BuiltInFunction.clear         = BuiltInFunction("clear")
BuiltInFunction.is_number     = BuiltInFunction("is_number")
BuiltInFunction.is_string     = BuiltInFunction("is_string")
BuiltInFunction.is_list       = BuiltInFunction("is_list")
BuiltInFunction.is_function   = BuiltInFunction("is_function")
BuiltInFunction.append        = BuiltInFunction("append")
BuiltInFunction.pop           = BuiltInFunction("pop")
BuiltInFunction.hang = BuiltInFunction("hang")
BuiltInFunction.extend        = BuiltInFunction("extend")
BuiltInFunction.len             = BuiltInFunction("len")
BuiltInFunction.run             = BuiltInFunction("run")
BuiltInFunction.python        = BuiltInFunction("python")
BuiltInFunction.python_import = BuiltInFunction("python_import")
BuiltInFunction.read_file     = BuiltInFunction("read_file")
BuiltInFunction.open_window   = BuiltInFunction("open_window")
BuiltInFunction.close_window  = BuiltInFunction("close_window")
BuiltInFunction.window_width  = BuiltInFunction("window_width")
BuiltInFunction.window_height = BuiltInFunction("window_height")
BuiltInFunction.resize_window = BuiltInFunction("resize_window")
BuiltInFunction.clear_window  = BuiltInFunction("clear_window")
BuiltInFunction.create_button = BuiltInFunction("create_button")
BuiltInFunction.create_text   = BuiltInFunction("create_text")

BuiltInFunction.math_acos = BuiltInFunction("math_acos")
BuiltInFunction.math_acosh   = BuiltInFunction("math_acosh")
BuiltInFunction.math_asin   = BuiltInFunction("math_asin")
BuiltInFunction.math_asinh   = BuiltInFunction("math_asinh")
BuiltInFunction.math_atan   = BuiltInFunction("math_atan")
BuiltInFunction.math_atanh   = BuiltInFunction("math_atanh")
BuiltInFunction.math_atan2   = BuiltInFunction("math_atan2")
BuiltInFunction.math_cbrt   = BuiltInFunction("math_cbrt")
BuiltInFunction.math_ceil   = BuiltInFunction("math_ceil")
BuiltInFunction.math_cos   = BuiltInFunction("math_cos")
BuiltInFunction.math_cosh   = BuiltInFunction("math_cosh")
BuiltInFunction.math_degrees   = BuiltInFunction("math_degrees")
BuiltInFunction.math_erf   = BuiltInFunction("math_erf")
BuiltInFunction.math_erfc   = BuiltInFunction("math_erfc")
BuiltInFunction.math_exp   = BuiltInFunction("math_exp")
BuiltInFunction.math_expm1  = BuiltInFunction("math_expm1")
BuiltInFunction.math_fabs   =  BuiltInFunction("math_fabs")
BuiltInFunction.math_factorial   = BuiltInFunction("math_factorial")
BuiltInFunction.math_floor   = BuiltInFunction("math_floor")
BuiltInFunction.math_gamma   = BuiltInFunction("math_gamma")
BuiltInFunction.math_lgamma   = BuiltInFunction("math_lgamma")
BuiltInFunction.math_log   = BuiltInFunction("math_log")
BuiltInFunction.math_log10   = BuiltInFunction("math_log10")
BuiltInFunction.math_log1p   = BuiltInFunction("math_log1p")
BuiltInFunction.math_log2   = BuiltInFunction("math_log2")
BuiltInFunction.math_modf   = BuiltInFunction("math_modf")
BuiltInFunction.math_pow   = BuiltInFunction("math_pow")
BuiltInFunction.math_radians   = BuiltInFunction("math_radians")
BuiltInFunction.math_sin  = BuiltInFunction("math_sin")
BuiltInFunction.math_sinh  = BuiltInFunction("math_sinh")
BuiltInFunction.math_sqrt   = BuiltInFunction("math_sqrt")
BuiltInFunction.math_tan   = BuiltInFunction("math_tan")
BuiltInFunction.math_tanh  = BuiltInFunction("math_tanh")
BuiltInFunction.math_trunc   = BuiltInFunction("math_trunc")

BuiltInFunction.str_len = BuiltInFunction("str_len")
BuiltInFunction.str_lower = BuiltInFunction("str_lower")
BuiltInFunction.str_upper = BuiltInFunction("str_upper")
BuiltInFunction.str_split = BuiltInFunction("str_split")
BuiltInFunction.str_strip = BuiltInFunction("str_strip")
BuiltInFunction.str_lstrip = BuiltInFunction("str_lstrip")
BuiltInFunction.str_rstrip = BuiltInFunction("str_rstrip")
BuiltInFunction.str_join = BuiltInFunction("str_join")
BuiltInFunction.str_replace = BuiltInFunction("str_replace")
BuiltInFunction.str_startswith = BuiltInFunction("str_startswith")
BuiltInFunction.str_endswith = BuiltInFunction("str_endswith")
BuiltInFunction.writefile = BuiltInFunction("writefile")
BuiltInFunction.exit = BuiltInFunction("exit")
BuiltInFunction.import_ = BuiltInFunction("import")
BuiltInFunction.eval = BuiltInFunction("eval")

BuiltInFunction.delay = BuiltInFunction("delay")
class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None
class SymbolTable:
  def __init__(self, parent=None):
    self.symbols = {}
    self.parent = parent

  def get(self, name):
    value = self.symbols.get(name, None)
    if value == None and self.parent:
      return self.parent.get(name)
    return value

  def set(self, name, value):
    self.symbols[name] = value

  def remove(self, name):
    del self.symbols[name]
class Interpreter:
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')

  def visit_NumberNode(self, node, context):
    return RTResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_StringNode(self, node, context):
    return RTResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ListNode(self, node, context):
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RTError(
        node.pos_start, node.pos_end,
        f"'{var_name}' is not defined",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  def visit_VarAssignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinOpNode(self, node, context):
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    if node.op_tok.type == TT_PLUS:
      result, error = left.added_to(right)
    elif node.op_tok.type == TT_MINUS:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == TT_MUL:
      result, error = left.multed_by(right)
    elif node.op_tok.type == TT_DIV:
      result, error = left.dived_by(right)
    elif node.op_tok.type == TT_POW:
      result, error = left.powed_by(right)
    elif node.op_tok.type == TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(TT_KEYWORD, 'and'):
      result, error = left.anded_by(right)
    elif node.op_tok.matches(TT_KEYWORD, 'or'):
      result, error = left.ored_by(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  def visit_UnaryOpNode(self, node, context):
    res = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    if node.op_tok.type == TT_MINUS:
      number, error = number.multed_by(Number(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'not'):
      number, error = number.notted()

    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  def visit_IfNode(self, node, context):
    res = RTResult()

    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Number.null if should_return_null else expr_value)

    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Number.null if should_return_null else expr_value)

    return res.success(Number.null)

  def visit_ForNode(self, node, context):
    res = RTResult()
    elements = []

    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res

    end_value = res.register(self.visit(node.end_value_node, context))
    if res.should_return(): return res

    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
    else:
      step_value = Number(1)

    i = start_value.value

    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value

    while condition():
      context.symbol_table.set(node.var_name_tok.value, Number(i))
      i += step_value.value

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue

      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_WhileNode(self, node, context):
    res = RTResult()
    elements = []

    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      if not condition.is_true():
        break

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue

      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_FuncDefNode(self, node, context):
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node, context):
    res = RTResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  def visit_ReturnNode(self, node, context):
    res = RTResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Number.null

    return res.success_return(value)

  def visit_ContinueNode(self, node, context):
    return RTResult().success_continue()

  def visit_BreakNode(self, node, context):
    return RTResult().success_break()

  


#######################################
# SYMBOL TABLE                        #
#######################################

global_symbol_table = SymbolTable()
# Basic globals
global_symbol_table.set("Null", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("math_pi", Number.math_PI)
# Basic functions
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_num", BuiltInFunction.is_number)
global_symbol_table.set("is_str", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_func", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("hang", BuiltInFunction.hang)
global_symbol_table.set("exit", BuiltInFunction.exit)
global_symbol_table.set("eval", BuiltInFunction.eval)
# Python integration
global_symbol_table.set("python", BuiltInFunction.python)
global_symbol_table.set("py", BuiltInFunction.python)
global_symbol_table.set("py_import", BuiltInFunction.python_import)
# IO
global_symbol_table.set("readfile", BuiltInFunction.read_file)
global_symbol_table.set("writefile", BuiltInFunction.writefile)
# GUI
global_symbol_table.set("openwindow", BuiltInFunction.open_window)
global_symbol_table.set("closewindow", BuiltInFunction.close_window)
global_symbol_table.set("window_width", BuiltInFunction.window_width)
global_symbol_table.set("window_height", BuiltInFunction.window_height)
global_symbol_table.set("window_resize", BuiltInFunction.resize_window)
global_symbol_table.set("window_clear", BuiltInFunction.clear_window)
global_symbol_table.set("window_create_button", BuiltInFunction.create_button)
global_symbol_table.set("window_create_text", BuiltInFunction.create_text)
# Fancy math
global_symbol_table.set("math_e", Number.e)
global_symbol_table.set("math_inf", Number.inf)
global_symbol_table.set("math_nan", Number.nan)
global_symbol_table.set("math_tau", Number.tau)
global_symbol_table.set("math_acos", BuiltInFunction.math_acos)
global_symbol_table.set("math_acosh", BuiltInFunction.math_acosh)
global_symbol_table.set("math_asin", BuiltInFunction.math_asin)
global_symbol_table.set("math_asinh", BuiltInFunction.math_asinh)
global_symbol_table.set("math_atan", BuiltInFunction.math_atan)
global_symbol_table.set("math_atanh", BuiltInFunction.math_atanh)
global_symbol_table.set("math_atan2", BuiltInFunction.math_atan2)
global_symbol_table.set("math_cbrt", BuiltInFunction.math_cbrt)
global_symbol_table.set("math_ceil", BuiltInFunction.math_ceil)
global_symbol_table.set("math_cos", BuiltInFunction.math_cos)
global_symbol_table.set("math_cosh", BuiltInFunction.math_cosh)
global_symbol_table.set("math_degrees", BuiltInFunction.math_degrees)
global_symbol_table.set("math_erf", BuiltInFunction.math_erf)
global_symbol_table.set("math_erfc", BuiltInFunction.math_erfc)
global_symbol_table.set("math_exp", BuiltInFunction.math_exp)
global_symbol_table.set("math_expm1", BuiltInFunction.math_expm1)
global_symbol_table.set("math_fabs", BuiltInFunction.math_fabs)
global_symbol_table.set("math_factorial", BuiltInFunction.math_factorial)
global_symbol_table.set("math_floor", BuiltInFunction.math_floor)
global_symbol_table.set("math_gamma", BuiltInFunction.math_gamma)
global_symbol_table.set("math_lgamma", BuiltInFunction.math_lgamma)
global_symbol_table.set("math_log", BuiltInFunction.math_log)
global_symbol_table.set("math_log10", BuiltInFunction.math_log10)
global_symbol_table.set("math_log1p", BuiltInFunction.math_log1p)
global_symbol_table.set("math_log2", BuiltInFunction.math_log2)
global_symbol_table.set("math_modf", BuiltInFunction.math_modf)
global_symbol_table.set("math_pow", BuiltInFunction.math_pow)
global_symbol_table.set("math_radians", BuiltInFunction.math_radians)
global_symbol_table.set("math_sin", BuiltInFunction.math_sin)
global_symbol_table.set("math_sinh", BuiltInFunction.math_sinh)
global_symbol_table.set("math_sqrt", BuiltInFunction.math_sqrt)
global_symbol_table.set("math_tan", BuiltInFunction.math_tan)
global_symbol_table.set("math_tanh", BuiltInFunction.math_tanh)
global_symbol_table.set("math_trunc", BuiltInFunction.math_trunc)
# String functions
global_symbol_table.set("str_len", BuiltInFunction.str_len)
global_symbol_table.set("str_lower", BuiltInFunction.str_lower)
global_symbol_table.set("str_upper", BuiltInFunction.str_upper)
global_symbol_table.set("str_split", BuiltInFunction.str_split)
global_symbol_table.set("str_join", BuiltInFunction.str_join)
global_symbol_table.set("str_strip", BuiltInFunction.str_strip)
global_symbol_table.set("str_lstrip", BuiltInFunction.str_lstrip)
global_symbol_table.set("str_rstrip", BuiltInFunction.str_rstrip)
global_symbol_table.set("str_startswith", BuiltInFunction.str_startswith)
global_symbol_table.set("str_endswith", BuiltInFunction.str_endswith)
global_symbol_table.set("str_replace", BuiltInFunction.str_replace)
# Packaging
global_symbol_table.set("import", BuiltInFunction.import_)
# Utils
global_symbol_table.set("delay", BuiltInFunction.delay)


def run(fn, text):
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error


def installPkg(pkg): 
  
  pkg_path = os.path.join(os.path.dirname(__file__), 'packages', pkg)
  if os.path.exists(pkg_path):
    print("Package '%s' already installed." % pkg)
    return 0  
  else:
    os.mkdir(pkg_path)
    cloud_url = 'https://raw.githubusercontent.com/HENRYMARTIN5/SolutionPackages/main/' + pkg + '/'
    print("Downloading package '%s'..." % pkg)

    print("Fetching dependencies...")
    dependencies = []
    try:
      with urllib.request.urlopen(cloud_url + 'deps') as f:
        if f.code == 200:
          dependencies = f.read().decode('utf-8').splitlines()
        else:
          print("Package '%s' does not exist." % pkg)
          return
    except urllib.error.HTTPError:
      print("Package '%s' does not exist." % pkg)
      return
    for dependency in dependencies:
      if dependency.startswith('#'):
        pass
      elif dependency.startswith('pip:'):
        os.system('pip install ' + dependency[4:])
      elif dependency != '':
        installPkg(dependency)
      else:
        print("Package '%s' does not exist." % pkg)
        return
    
    print("Downloading '%s.ph'..." % pkg)
    with urllib.request.urlopen(cloud_url + pkg+".ph") as f:
      ph = f.read().decode('utf-8')
      with open(os.path.join(pkg_path,pkg+".ph"), "w+") as f:
        f.write(ph)

    print("Downloading 'init.py'...")
    with urllib.request.urlopen(cloud_url + 'init.py') as f:
      init = f.read().decode('utf-8')
      with open(os.path.join(pkg_path,'init.py'), "w+") as f:
        f.write(init)
    
    print("Downloading setup files...")
    with urllib.request.urlopen(cloud_url + 'setup.py') as f:
      setup_py = f.read().decode('utf-8')
      with open(os.path.join(pkg_path,"setup.py"), "w+") as f:
        f.write(setup_py)
      print("Installing package '%s'..." % pkg)
      exec(compile(setup_py))

    

    print("Package '%s' installed!" % pkg)
    return 1
    
    



def main():
  try:
    sys.argv[1]
    if sys.argv[1]:
      if sys.argv[1] == 'install':
        if len(sys.argv) > 2:
          installPkg(sys.argv[2])
          return
        else:
          print("Please specify a package name.")
          return
      result, error = run(sys.argv[1], "run(\"" + sys.argv[1] + "\")")
      if error:
        print(error.as_string())
  except:
    try:
      while True:
        text = input('phlang > ')
        if text.strip() == "": continue
        result, error = run('<stdin>', text)

        if error:
          print(error.as_string())
        elif result:
          if len(result.elements) == 1:
            print(repr(result.elements[0]))
          else:
            print(repr(result))

    except Exception as e:
      print("Uncaught exception:", e)
      main()

if __name__ == "__main__":
  main()



######################################################################################
# Lo, and behold. Thou havest reachest the end of this script. How did you get here? #
# Well, I guess you could have not read the actual code.                             #
# If you actually did, good for you. Your head must hurt by now.                     #
# Hope you use pHLang well.                                                          #
#                                                                                    #
# - Henry Martin                                                                     #
######################################################################################