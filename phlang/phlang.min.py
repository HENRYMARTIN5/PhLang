_Az='delay'
_Ay='key_press'
_Ax='key_type'
_Aw='mouse_scroll'
_Av='mouse_move'
_Au='mouse_click_png'
_At='mouse_click'
_As='import'
_Ar='writefile'
_Aq='str_endswith'
_Ap='str_startswith'
_Ao='str_replace'
_An='str_join'
_Am='str_rstrip'
_Al='str_lstrip'
_Ak='str_strip'
_Aj='str_split'
_Ai='str_upper'
_Ah='str_lower'
_Ag='str_len'
_Af='math_trunc'
_Ae='math_tanh'
_Ad='math_tan'
_Ac='math_sqrt'
_Ab='math_sinh'
_Aa='math_sin'
_AZ='math_radians'
_AY='math_pow'
_AX='math_modf'
_AW='math_log2'
_AV='math_log1p'
_AU='math_log10'
_AT='math_log'
_AS='math_lgamma'
_AR='math_gamma'
_AQ='math_floor'
_AP='math_factorial'
_AO='math_fabs'
_AN='math_expm1'
_AM='math_exp'
_AL='math_erfc'
_AK='math_erf'
_AJ='math_degrees'
_AI='math_cosh'
_AH='math_cos'
_AG='math_ceil'
_AF='math_cbrt'
_AE='math_atan2'
_AD='math_atanh'
_AC='math_atan'
_AB='math_asinh'
_AA='math_asin'
_A9='math_acosh'
_A8='math_acos'
_A7='window_height'
_A6='window_width'
_A5='python'
_A4='extend'
_A3='append'
_A2='is_list'
_A1='clear'
_A0='input_int'
_z='input'
_y='print_ret'
_x='print'
_w='time'
_v='pngname'
_u='packages'
_t='content'
_s='file_name'
_r='functionname'
_q='height'
_p='width'
_o='background'
_n='title'
_m='listB'
_l='listA'
_k='index'
_j='exec'
_i='Element at this index could not be removed from list because index is out of bounds'
_h='break'
_g='continue'
_f='return'
_e='step'
_d='else'
_c='var'
_b='\n\n'
_a='.ph'
_Z='First argument must be list'
_Y='cls'
_X='func'
_W='while'
_V='for'
_U='elif'
_T='if'
_S='not'
_R='or'
_Q='and'
_P='\t'
_O='key'
_N='text'
_M='"'
_L='then'
_K='='
_J='fn'
_I='list'
_H='end'
_G='\n'
_F=False
_E=True
_D='y'
_C='value'
_B='x'
_A=None
import os,string,time,math
from importlib import import_module
import tkinter as tk,sys,urllib.request,pyautogui
execGlobals={}
execLocals={}
DIGITS='0123456789'
LETTERS=string.ascii_letters
LETTERS_DIGITS=LETTERS+DIGITS
WINDOW=_A
def createWindow(title,background):global WINDOW;WINDOW=tk.Tk();WINDOW.title(title);WINDOW.geometry('600x400');WINDOW.resizable(0,0);WINDOW.protocol('WM_DELETE_WINDOW',sys.exit);WINDOW.configure(background=background)
def closeWindow():WINDOW.destroy()
def getWindowWidth():return WINDOW.winfo_width()
def getWindowHeight():return WINDOW.winfo_height()
def resizeWindow(height,width):WINDOW.geometry(f"{width}x{height}")
def clearWindow():WINDOW.delete('all')
def addButton(text,x,y,pyfunc):button=tk.Button(WINDOW,text=text,command=lambda:run('<onClick>',pyfunc));button.place(x=x,y=y)
def addText(text,x,y):text=tk.Label(WINDOW,text=text);text.place(x=x,y=y)
def hang():
	while _E:0
def string_with_arrows(text,pos_start,pos_end):
	result='';idx_start=max(text.rfind(_G,0,pos_start.idx),0);idx_end=text.find(_G,idx_start+1)
	if idx_end<0:idx_end=len(text)
	line_count=pos_end.ln-pos_start.ln+1
	for i in range(line_count):
		line=text[idx_start:idx_end];col_start=pos_start.col if i==0 else 0;col_end=pos_end.col if i==line_count-1 else len(line)-1;result+=line+_G;result+=' '*col_start+'^'*(col_end-col_start);idx_start=idx_end;idx_end=text.find(_G,idx_start+1)
		if idx_end<0:idx_end=len(text)
	return result.replace(_P,'')
class Error:
	def __init__(self,pos_start,pos_end,error_name,details):self.pos_start=pos_start;self.pos_end=pos_end;self.error_name=error_name;self.details=details
	def as_string(self):result=f"{self.error_name}: {self.details}\n";result+=f"File {self.pos_start.fn}, line {self.pos_start.ln+1}";result+=_b+string_with_arrows(self.pos_start.ftxt,self.pos_start,self.pos_end);return result
class IllegalCharError(Error):
	def __init__(self,pos_start,pos_end,details):super().__init__(pos_start,pos_end,'Illegal Character',details)
class ExpectedCharError(Error):
	def __init__(self,pos_start,pos_end,details):super().__init__(pos_start,pos_end,'Expected Character',details)
class InvalidSyntaxError(Error):
	def __init__(self,pos_start,pos_end,details=''):super().__init__(pos_start,pos_end,'Invalid Syntax',details)
class RTError(Error):
	def __init__(self,pos_start,pos_end,details,context):super().__init__(pos_start,pos_end,'Runtime Error',details);self.context=context
	def as_string(self):result=self.generate_traceback();result+=f"{self.error_name}: {self.details}";result+=_b+string_with_arrows(self.pos_start.ftxt,self.pos_start,self.pos_end);return result
	def generate_traceback(self):
		result='';pos=self.pos_start;ctx=self.context
		while ctx:result=f"  File {pos.fn}, line {str(pos.ln+1)}, in {ctx.display_name}\n"+result;pos=ctx.parent_entry_pos;ctx=ctx.parent
		return'Traceback (most recent call):\n'+result
class Position:
	def __init__(self,idx,ln,col,fn,ftxt):self.idx=idx;self.ln=ln;self.col=col;self.fn=fn;self.ftxt=ftxt
	def advance(self,current_char=_A):
		self.idx+=1;self.col+=1
		if current_char==_G:self.ln+=1;self.col=0
		return self
	def copy(self):return Position(self.idx,self.ln,self.col,self.fn,self.ftxt)
TT_INT='int'
TT_FLOAT='float'
TT_STRING='string'
TT_IDENTIFIER='identifier'
TT_KEYWORD='keyword'
TT_PLUS='plus'
TT_MINUS='minus'
TT_MUL='mul'
TT_DIV='div'
TT_POW='pow'
TT_EQ='eq'
TT_LPAREN='lparen'
TT_RPAREN='rparen'
TT_LSQUARE='lsquare'
TT_RSQUARE='rsquare'
TT_EE='ee'
TT_NE='ne'
TT_LT='lt'
TT_GT='gt'
TT_LTE='lte'
TT_GTE='gte'
TT_COMMA='comma'
TT_ARROW='arrow'
TT_NEWLINE='newline'
TT_EOF='eof'
KEYWORDS=[_c,_Q,_R,_S,_T,_U,_d,_V,'to',_e,_W,_X,_L,_H,_f,_g,_h]
class Token:
	def __init__(self,type_,value=_A,pos_start=_A,pos_end=_A):
		self.type=type_;self.value=value
		if pos_start:self.pos_start=pos_start.copy();self.pos_end=pos_start.copy();self.pos_end.advance()
		if pos_end:self.pos_end=pos_end.copy()
	def matches(self,type_,value):return self.type==type_ and self.value==value
	def __repr__(self):
		if self.value:return f"{self.type}:{self.value}"
		return f"{self.type}"
class Lexer:
	def __init__(self,fn,text):self.fn=fn;self.text=text;self.pos=Position(-1,0,-1,fn,text);self.current_char=_A;self.advance()
	def advance(self):self.pos.advance(self.current_char);self.current_char=self.text[self.pos.idx]if self.pos.idx<len(self.text)else _A
	def make_tokens(self):
		A="'";tokens=[]
		while self.current_char!=_A:
			if self.current_char in' \t':self.advance()
			elif self.current_char=='#':self.skip_comment()
			elif self.current_char in';\n':tokens.append(Token(TT_NEWLINE,pos_start=self.pos));self.advance()
			elif self.current_char in DIGITS:tokens.append(self.make_number())
			elif self.current_char in LETTERS:tokens.append(self.make_identifier())
			elif self.current_char==_M:tokens.append(self.make_string())
			elif self.current_char=='+':tokens.append(Token(TT_PLUS,pos_start=self.pos));self.advance()
			elif self.current_char=='-':tokens.append(self.make_minus_or_arrow())
			elif self.current_char=='*':tokens.append(Token(TT_MUL,pos_start=self.pos));self.advance()
			elif self.current_char=='/':tokens.append(Token(TT_DIV,pos_start=self.pos));self.advance()
			elif self.current_char=='^':tokens.append(Token(TT_POW,pos_start=self.pos));self.advance()
			elif self.current_char=='(':tokens.append(Token(TT_LPAREN,pos_start=self.pos));self.advance()
			elif self.current_char==')':tokens.append(Token(TT_RPAREN,pos_start=self.pos));self.advance()
			elif self.current_char=='[':tokens.append(Token(TT_LSQUARE,pos_start=self.pos));self.advance()
			elif self.current_char==']':tokens.append(Token(TT_RSQUARE,pos_start=self.pos));self.advance()
			elif self.current_char=='!':
				token,error=self.make_not_equals()
				if error:return[],error
				tokens.append(token)
			elif self.current_char==_K:tokens.append(self.make_equals())
			elif self.current_char=='<':tokens.append(self.make_less_than())
			elif self.current_char=='>':tokens.append(self.make_greater_than())
			elif self.current_char==',':tokens.append(Token(TT_COMMA,pos_start=self.pos));self.advance()
			else:pos_start=self.pos.copy();char=self.current_char;self.advance();return[],IllegalCharError(pos_start,self.pos,A+char+A)
		tokens.append(Token(TT_EOF,pos_start=self.pos));return tokens,_A
	def make_number(self):
		A='.';num_str='';dot_count=0;pos_start=self.pos.copy()
		while self.current_char!=_A and self.current_char in DIGITS+A:
			if self.current_char==A:
				if dot_count==1:break
				dot_count+=1
			num_str+=self.current_char;self.advance()
		if dot_count==0:return Token(TT_INT,int(num_str),pos_start,self.pos)
		else:return Token(TT_FLOAT,float(num_str),pos_start,self.pos)
	def make_string(self):
		string='';pos_start=self.pos.copy();escape_character=_F;self.advance();escape_characters={'n':_G,'t':_P,_M:_M}
		while self.current_char!=_A and(self.current_char!=_M or escape_character):
			if escape_character:string+=escape_characters.get(self.current_char,self.current_char)
			elif self.current_char=='\\':escape_character=_E;self.advance();continue
			else:string+=self.current_char
			self.advance();escape_character=_F
		self.advance();return Token(TT_STRING,string,pos_start,self.pos)
	def make_identifier(self):
		id_str='';pos_start=self.pos.copy()
		while self.current_char!=_A and self.current_char in LETTERS_DIGITS+'_':id_str+=self.current_char;self.advance()
		tok_type=TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER;return Token(tok_type,id_str,pos_start,self.pos)
	def make_minus_or_arrow(self):
		tok_type=TT_MINUS;pos_start=self.pos.copy();self.advance()
		if self.current_char=='>':self.advance();tok_type=TT_ARROW
		return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
	def make_not_equals(self):
		pos_start=self.pos.copy();self.advance()
		if self.current_char==_K:self.advance();return Token(TT_NE,pos_start=pos_start,pos_end=self.pos),_A
		self.advance();return _A,ExpectedCharError(pos_start,self.pos,"'=' (after '!')")
	def make_equals(self):
		tok_type=TT_EQ;pos_start=self.pos.copy();self.advance()
		if self.current_char==_K:self.advance();tok_type=TT_EE
		return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
	def make_less_than(self):
		tok_type=TT_LT;pos_start=self.pos.copy();self.advance()
		if self.current_char==_K:self.advance();tok_type=TT_LTE
		return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
	def make_greater_than(self):
		tok_type=TT_GT;pos_start=self.pos.copy();self.advance()
		if self.current_char==_K:self.advance();tok_type=TT_GTE
		return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
	def skip_comment(self):
		self.advance()
		while self.current_char!=_G:self.advance()
		self.advance()
class NumberNode:
	def __init__(self,tok):self.tok=tok;self.pos_start=self.tok.pos_start;self.pos_end=self.tok.pos_end
	def __repr__(self):return f"{self.tok}"
class StringNode:
	def __init__(self,tok):self.tok=tok;self.pos_start=self.tok.pos_start;self.pos_end=self.tok.pos_end
	def __repr__(self):return f"{self.tok}"
class ListNode:
	def __init__(self,element_nodes,pos_start,pos_end):self.element_nodes=element_nodes;self.pos_start=pos_start;self.pos_end=pos_end
class VarAccessNode:
	def __init__(self,var_name_tok):self.var_name_tok=var_name_tok;self.pos_start=self.var_name_tok.pos_start;self.pos_end=self.var_name_tok.pos_end
class VarAssignNode:
	def __init__(self,var_name_tok,value_node):self.var_name_tok=var_name_tok;self.value_node=value_node;self.pos_start=self.var_name_tok.pos_start;self.pos_end=self.value_node.pos_end
class BinOpNode:
	def __init__(self,left_node,op_tok,right_node):self.left_node=left_node;self.op_tok=op_tok;self.right_node=right_node;self.pos_start=self.left_node.pos_start;self.pos_end=self.right_node.pos_end
	def __repr__(self):return f"({self.left_node}, {self.op_tok}, {self.right_node})"
class UnaryOpNode:
	def __init__(self,op_tok,node):self.op_tok=op_tok;self.node=node;self.pos_start=self.op_tok.pos_start;self.pos_end=node.pos_end
	def __repr__(self):return f"({self.op_tok}, {self.node})"
class IfNode:
	def __init__(self,cases,else_case):self.cases=cases;self.else_case=else_case;self.pos_start=self.cases[0][0].pos_start;self.pos_end=(self.else_case or self.cases[len(self.cases)-1])[0].pos_end
class ForNode:
	def __init__(self,var_name_tok,start_value_node,end_value_node,step_value_node,body_node,should_return_null):self.var_name_tok=var_name_tok;self.start_value_node=start_value_node;self.end_value_node=end_value_node;self.step_value_node=step_value_node;self.body_node=body_node;self.should_return_null=should_return_null;self.pos_start=self.var_name_tok.pos_start;self.pos_end=self.body_node.pos_end
class WhileNode:
	def __init__(self,condition_node,body_node,should_return_null):self.condition_node=condition_node;self.body_node=body_node;self.should_return_null=should_return_null;self.pos_start=self.condition_node.pos_start;self.pos_end=self.body_node.pos_end
class FuncDefNode:
	def __init__(self,var_name_tok,arg_name_toks,body_node,should_auto_return):
		self.var_name_tok=var_name_tok;self.arg_name_toks=arg_name_toks;self.body_node=body_node;self.should_auto_return=should_auto_return
		if self.var_name_tok:self.pos_start=self.var_name_tok.pos_start
		elif len(self.arg_name_toks)>0:self.pos_start=self.arg_name_toks[0].pos_start
		else:self.pos_start=self.body_node.pos_start
		self.pos_end=self.body_node.pos_end
class CallNode:
	def __init__(self,node_to_call,arg_nodes):
		self.node_to_call=node_to_call;self.arg_nodes=arg_nodes;self.pos_start=self.node_to_call.pos_start
		if len(self.arg_nodes)>0:self.pos_end=self.arg_nodes[len(self.arg_nodes)-1].pos_end
		else:self.pos_end=self.node_to_call.pos_end
class ReturnNode:
	def __init__(self,node_to_return,pos_start,pos_end):self.node_to_return=node_to_return;self.pos_start=pos_start;self.pos_end=pos_end
class ContinueNode:
	def __init__(self,pos_start,pos_end):self.pos_start=pos_start;self.pos_end=pos_end
class BreakNode:
	def __init__(self,pos_start,pos_end):self.pos_start=pos_start;self.pos_end=pos_end
class ParseResult:
	def __init__(self):self.error=_A;self.node=_A;self.last_registered_advance_count=0;self.advance_count=0;self.to_reverse_count=0
	def register_advancement(self):self.last_registered_advance_count=1;self.advance_count+=1
	def register(self,res):
		self.last_registered_advance_count=res.advance_count;self.advance_count+=res.advance_count
		if res.error:self.error=res.error
		return res.node
	def try_register(self,res):
		if res.error:self.to_reverse_count=res.advance_count;return _A
		return self.register(res)
	def success(self,node):self.node=node;return self
	def failure(self,error):
		if not self.error or self.last_registered_advance_count==0:self.error=error
		return self
class Parser:
	def __init__(self,tokens):self.tokens=tokens;self.tok_idx=-1;self.advance()
	def advance(self):self.tok_idx+=1;self.update_current_tok();return self.current_tok
	def reverse(self,amount=1):self.tok_idx-=amount;self.update_current_tok();return self.current_tok
	def update_current_tok(self):
		if self.tok_idx>=0 and self.tok_idx<len(self.tokens):self.current_tok=self.tokens[self.tok_idx]
	def parse(self):
		res=self.statements()
		if not res.error and self.current_tok.type!=TT_EOF:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,'Token cannot appear after previous tokens'))
		return res
	def statements(self):
		res=ParseResult();statements=[];pos_start=self.current_tok.pos_start.copy()
		while self.current_tok.type==TT_NEWLINE:res.register_advancement();self.advance()
		statement=res.register(self.statement())
		if res.error:return res
		statements.append(statement);more_statements=_E
		while _E:
			newline_count=0
			while self.current_tok.type==TT_NEWLINE:res.register_advancement();self.advance();newline_count+=1
			if newline_count==0:more_statements=_F
			if not more_statements:break
			statement=res.try_register(self.statement())
			if not statement:self.reverse(res.to_reverse_count);more_statements=_F;continue
			statements.append(statement)
		return res.success(ListNode(statements,pos_start,self.current_tok.pos_end.copy()))
	def statement(self):
		res=ParseResult();pos_start=self.current_tok.pos_start.copy()
		if self.current_tok.matches(TT_KEYWORD,_f):
			res.register_advancement();self.advance();expr=res.try_register(self.expr())
			if not expr:self.reverse(res.to_reverse_count)
			return res.success(ReturnNode(expr,pos_start,self.current_tok.pos_start.copy()))
		if self.current_tok.matches(TT_KEYWORD,_g):res.register_advancement();self.advance();return res.success(ContinueNode(pos_start,self.current_tok.pos_start.copy()))
		if self.current_tok.matches(TT_KEYWORD,_h):res.register_advancement();self.advance();return res.success(BreakNode(pos_start,self.current_tok.pos_start.copy()))
		expr=res.register(self.expr())
		if res.error:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected 'return', 'continue', 'break', 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'NOT'"))
		return res.success(expr)
	def expr(self):
		res=ParseResult()
		if self.current_tok.matches(TT_KEYWORD,_c):
			res.register_advancement();self.advance()
			if self.current_tok.type!=TT_IDENTIFIER:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,'Expected identifier'))
			var_name=self.current_tok;res.register_advancement();self.advance()
			if self.current_tok.type!=TT_EQ:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected '='"))
			res.register_advancement();self.advance();expr=res.register(self.expr())
			if res.error:return res
			return res.success(VarAssignNode(var_name,expr))
		node=res.register(self.bin_op(self.comp_expr,((TT_KEYWORD,_Q),(TT_KEYWORD,_R))))
		if res.error:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'NOT'"))
		return res.success(node)
	def comp_expr(self):
		res=ParseResult()
		if self.current_tok.matches(TT_KEYWORD,_S):
			op_tok=self.current_tok;res.register_advancement();self.advance();node=res.register(self.comp_expr())
			if res.error:return res
			return res.success(UnaryOpNode(op_tok,node))
		node=res.register(self.bin_op(self.arith_expr,(TT_EE,TT_NE,TT_LT,TT_GT,TT_LTE,TT_GTE)))
		if res.error:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'func' or 'NOT'"))
		return res.success(node)
	def arith_expr(self):return self.bin_op(self.term,(TT_PLUS,TT_MINUS))
	def term(self):return self.bin_op(self.factor,(TT_MUL,TT_DIV))
	def factor(self):
		res=ParseResult();tok=self.current_tok
		if tok.type in(TT_PLUS,TT_MINUS):
			res.register_advancement();self.advance();factor=res.register(self.factor())
			if res.error:return res
			return res.success(UnaryOpNode(tok,factor))
		return self.power()
	def power(self):return self.bin_op(self.call,(TT_POW,),self.factor)
	def call(self):
		res=ParseResult();atom=res.register(self.atom())
		if res.error:return res
		if self.current_tok.type==TT_LPAREN:
			res.register_advancement();self.advance();arg_nodes=[]
			if self.current_tok.type==TT_RPAREN:res.register_advancement();self.advance()
			else:
				arg_nodes.append(res.register(self.expr()))
				if res.error:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected ')', 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'NOT'"))
				while self.current_tok.type==TT_COMMA:
					res.register_advancement();self.advance();arg_nodes.append(res.register(self.expr()))
					if res.error:return res
				if self.current_tok.type!=TT_RPAREN:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected ',' or ')'"))
				res.register_advancement();self.advance()
			return res.success(CallNode(atom,arg_nodes))
		return res.success(atom)
	def atom(self):
		res=ParseResult();tok=self.current_tok
		if tok.type in(TT_INT,TT_FLOAT):res.register_advancement();self.advance();return res.success(NumberNode(tok))
		elif tok.type==TT_STRING:res.register_advancement();self.advance();return res.success(StringNode(tok))
		elif tok.type==TT_IDENTIFIER:res.register_advancement();self.advance();return res.success(VarAccessNode(tok))
		elif tok.type==TT_LPAREN:
			res.register_advancement();self.advance();expr=res.register(self.expr())
			if res.error:return res
			if self.current_tok.type==TT_RPAREN:res.register_advancement();self.advance();return res.success(expr)
			else:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected ')'"))
		elif tok.type==TT_LSQUARE:
			list_expr=res.register(self.list_expr())
			if res.error:return res
			return res.success(list_expr)
		elif tok.matches(TT_KEYWORD,_T):
			if_expr=res.register(self.if_expr())
			if res.error:return res
			return res.success(if_expr)
		elif tok.matches(TT_KEYWORD,_V):
			for_expr=res.register(self.for_expr())
			if res.error:return res
			return res.success(for_expr)
		elif tok.matches(TT_KEYWORD,_W):
			while_expr=res.register(self.while_expr())
			if res.error:return res
			return res.success(while_expr)
		elif tok.matches(TT_KEYWORD,_X):
			func_def=res.register(self.func_def())
			if res.error:return res
			return res.success(func_def)
		return res.failure(InvalidSyntaxError(tok.pos_start,tok.pos_end,"Expected int, float, identifier, '+', '-', '(', '[', if', 'for', 'while', 'fun'"))
	def list_expr(self):
		res=ParseResult();element_nodes=[];pos_start=self.current_tok.pos_start.copy()
		if self.current_tok.type!=TT_LSQUARE:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected '['"))
		res.register_advancement();self.advance()
		if self.current_tok.type==TT_RSQUARE:res.register_advancement();self.advance()
		else:
			element_nodes.append(res.register(self.expr()))
			if res.error:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected ']', 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[' or 'not'"))
			while self.current_tok.type==TT_COMMA:
				res.register_advancement();self.advance();element_nodes.append(res.register(self.expr()))
				if res.error:return res
			if self.current_tok.type!=TT_RSQUARE:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected ',' or ']'"))
			res.register_advancement();self.advance()
		return res.success(ListNode(element_nodes,pos_start,self.current_tok.pos_end.copy()))
	def if_expr(self):
		res=ParseResult();all_cases=res.register(self.if_expr_cases(_T))
		if res.error:return res
		cases,else_case=all_cases;return res.success(IfNode(cases,else_case))
	def if_expr_b(self):return self.if_expr_cases(_U)
	def if_expr_c(self):
		res=ParseResult();else_case=_A
		if self.current_tok.matches(TT_KEYWORD,_d):
			res.register_advancement();self.advance()
			if self.current_tok.type==TT_NEWLINE:
				res.register_advancement();self.advance();statements=res.register(self.statements())
				if res.error:return res
				else_case=statements,_E
				if self.current_tok.matches(TT_KEYWORD,_H):res.register_advancement();self.advance()
				else:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected 'end'"))
			else:
				expr=res.register(self.statement())
				if res.error:return res
				else_case=expr,_F
		return res.success(else_case)
	def if_expr_b_or_c(self):
		res=ParseResult();cases,else_case=[],_A
		if self.current_tok.matches(TT_KEYWORD,_U):
			all_cases=res.register(self.if_expr_b())
			if res.error:return res
			cases,else_case=all_cases
		else:
			else_case=res.register(self.if_expr_c())
			if res.error:return res
		return res.success((cases,else_case))
	def if_expr_cases(self,case_keyword):
		res=ParseResult();cases=[];else_case=_A
		if not self.current_tok.matches(TT_KEYWORD,case_keyword):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected '{case_keyword}'"))
		res.register_advancement();self.advance();condition=res.register(self.expr())
		if res.error:return res
		if not self.current_tok.matches(TT_KEYWORD,_L):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'THEN'"))
		res.register_advancement();self.advance()
		if self.current_tok.type==TT_NEWLINE:
			res.register_advancement();self.advance();statements=res.register(self.statements())
			if res.error:return res
			cases.append((condition,statements,_E))
			if self.current_tok.matches(TT_KEYWORD,_H):res.register_advancement();self.advance()
			else:
				all_cases=res.register(self.if_expr_b_or_c())
				if res.error:return res
				new_cases,else_case=all_cases;cases.extend(new_cases)
		else:
			expr=res.register(self.statement())
			if res.error:return res
			cases.append((condition,expr,_F));all_cases=res.register(self.if_expr_b_or_c())
			if res.error:return res
			new_cases,else_case=all_cases;cases.extend(new_cases)
		return res.success((cases,else_case))
	def for_expr(self):
		res=ParseResult()
		if not self.current_tok.matches(TT_KEYWORD,_V):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'for'"))
		res.register_advancement();self.advance()
		if self.current_tok.type!=TT_IDENTIFIER:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected identifier"))
		var_name=self.current_tok;res.register_advancement();self.advance()
		if self.current_tok.type!=TT_EQ:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected '='"))
		res.register_advancement();self.advance();start_value=res.register(self.expr())
		if res.error:return res
		if not self.current_tok.matches(TT_KEYWORD,'to'):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'TO'"))
		res.register_advancement();self.advance();end_value=res.register(self.expr())
		if res.error:return res
		if self.current_tok.matches(TT_KEYWORD,_e):
			res.register_advancement();self.advance();step_value=res.register(self.expr())
			if res.error:return res
		else:step_value=_A
		if not self.current_tok.matches(TT_KEYWORD,_L):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'THEN'"))
		res.register_advancement();self.advance()
		if self.current_tok.type==TT_NEWLINE:
			res.register_advancement();self.advance();body=res.register(self.statements())
			if res.error:return res
			if not self.current_tok.matches(TT_KEYWORD,_H):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'end'"))
			res.register_advancement();self.advance();return res.success(ForNode(var_name,start_value,end_value,step_value,body,_E))
		body=res.register(self.statement())
		if res.error:return res
		return res.success(ForNode(var_name,start_value,end_value,step_value,body,_F))
	def while_expr(self):
		res=ParseResult()
		if not self.current_tok.matches(TT_KEYWORD,_W):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'while'"))
		res.register_advancement();self.advance();condition=res.register(self.expr())
		if res.error:return res
		if not self.current_tok.matches(TT_KEYWORD,_L):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'THEN'"))
		res.register_advancement();self.advance()
		if self.current_tok.type==TT_NEWLINE:
			res.register_advancement();self.advance();body=res.register(self.statements())
			if res.error:return res
			if not self.current_tok.matches(TT_KEYWORD,_H):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'end'"))
			res.register_advancement();self.advance();return res.success(WhileNode(condition,body,_E))
		body=res.register(self.statement())
		if res.error:return res
		return res.success(WhileNode(condition,body,_F))
	def func_def(self):
		res=ParseResult()
		if not self.current_tok.matches(TT_KEYWORD,_X):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'func'"))
		res.register_advancement();self.advance()
		if self.current_tok.type==TT_IDENTIFIER:
			var_name_tok=self.current_tok;res.register_advancement();self.advance()
			if self.current_tok.type!=TT_LPAREN:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected '('"))
		else:
			var_name_tok=_A
			if self.current_tok.type!=TT_LPAREN:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected identifier or '('"))
		res.register_advancement();self.advance();arg_name_toks=[]
		if self.current_tok.type==TT_IDENTIFIER:
			arg_name_toks.append(self.current_tok);res.register_advancement();self.advance()
			while self.current_tok.type==TT_COMMA:
				res.register_advancement();self.advance()
				if self.current_tok.type!=TT_IDENTIFIER:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected identifier"))
				arg_name_toks.append(self.current_tok);res.register_advancement();self.advance()
			if self.current_tok.type!=TT_RPAREN:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected ',' or ')'"))
		elif self.current_tok.type!=TT_RPAREN:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected identifier or ')'"))
		res.register_advancement();self.advance()
		if self.current_tok.type==TT_ARROW:
			res.register_advancement();self.advance();body=res.register(self.expr())
			if res.error:return res
			return res.success(FuncDefNode(var_name_tok,arg_name_toks,body,_E))
		if self.current_tok.type!=TT_NEWLINE:return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected '->' or NEWLINE"))
		res.register_advancement();self.advance();body=res.register(self.statements())
		if res.error:return res
		if not self.current_tok.matches(TT_KEYWORD,_H):return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,f"Expected 'end'"))
		res.register_advancement();self.advance();return res.success(FuncDefNode(var_name_tok,arg_name_toks,body,_F))
	def bin_op(self,func_a,ops,func_b=_A):
		if func_b==_A:func_b=func_a
		res=ParseResult();left=res.register(func_a())
		if res.error:return res
		while self.current_tok.type in ops or(self.current_tok.type,self.current_tok.value)in ops:
			op_tok=self.current_tok;res.register_advancement();self.advance();right=res.register(func_b())
			if res.error:return res
			left=BinOpNode(left,op_tok,right)
		return res.success(left)
class RTResult:
	def __init__(self):self.reset()
	def reset(self):self.value=_A;self.error=_A;self.func_return_value=_A;self.loop_should_continue=_F;self.loop_should_break=_F
	def register(self,res):self.error=res.error;self.func_return_value=res.func_return_value;self.loop_should_continue=res.loop_should_continue;self.loop_should_break=res.loop_should_break;return res.value
	def success(self,value):self.reset();self.value=value;return self
	def success_return(self,value):self.reset();self.func_return_value=value;return self
	def success_continue(self):self.reset();self.loop_should_continue=_E;return self
	def success_break(self):self.reset();self.loop_should_break=_E;return self
	def failure(self,error):self.reset();self.error=error;return self
	def should_return(self):return self.error or self.func_return_value or self.loop_should_continue or self.loop_should_break
class Value:
	def __init__(self):self.set_pos();self.set_context()
	def set_pos(self,pos_start=_A,pos_end=_A):self.pos_start=pos_start;self.pos_end=pos_end;return self
	def set_context(self,context=_A):self.context=context;return self
	def added_to(self,other):return _A,self.illegal_operation(other)
	def subbed_by(self,other):return _A,self.illegal_operation(other)
	def multed_by(self,other):return _A,self.illegal_operation(other)
	def dived_by(self,other):return _A,self.illegal_operation(other)
	def powed_by(self,other):return _A,self.illegal_operation(other)
	def get_comparison_eq(self,other):return _A,self.illegal_operation(other)
	def get_comparison_ne(self,other):return _A,self.illegal_operation(other)
	def get_comparison_lt(self,other):return _A,self.illegal_operation(other)
	def get_comparison_gt(self,other):return _A,self.illegal_operation(other)
	def get_comparison_lte(self,other):return _A,self.illegal_operation(other)
	def get_comparison_gte(self,other):return _A,self.illegal_operation(other)
	def anded_by(self,other):return _A,self.illegal_operation(other)
	def ored_by(self,other):return _A,self.illegal_operation(other)
	def notted(self):return _A,self.illegal_operation(other)
	def execute(self,args):return RTResult().failure(self.illegal_operation())
	def copy(self):raise Exception('No copy method defined')
	def is_true(self):return _F
	def illegal_operation(self,other=_A):
		if not other:other=self
		return RTError(self.pos_start,other.pos_end,'Illegal operation',self.context)
class Number(Value):
	def __init__(self,value):super().__init__();self.value=value
	def added_to(self,other):
		if isinstance(other,Number):return Number(self.value+other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def subbed_by(self,other):
		if isinstance(other,Number):return Number(self.value-other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def multed_by(self,other):
		if isinstance(other,Number):return Number(self.value*other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def dived_by(self,other):
		if isinstance(other,Number):
			if other.value==0:return _A,RTError(other.pos_start,other.pos_end,'Division by zero',self.context)
			return Number(self.value/other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def powed_by(self,other):
		if isinstance(other,Number):return Number(self.value**other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_eq(self,other):
		if isinstance(other,Number):return Number(int(self.value==other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_ne(self,other):
		if isinstance(other,Number):return Number(int(self.value!=other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_lt(self,other):
		if isinstance(other,Number):return Number(int(self.value<other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_gt(self,other):
		if isinstance(other,Number):return Number(int(self.value>other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_lte(self,other):
		if isinstance(other,Number):return Number(int(self.value<=other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_gte(self,other):
		if isinstance(other,Number):return Number(int(self.value>=other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def anded_by(self,other):
		if isinstance(other,Number):return Number(int(self.value and other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def ored_by(self,other):
		if isinstance(other,Number):return Number(int(self.value or other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def notted(self):return Number(1 if self.value==0 else 0).set_context(self.context),_A
	def copy(self):copy=Number(self.value);copy.set_pos(self.pos_start,self.pos_end);copy.set_context(self.context);return copy
	def is_true(self):return self.value!=0
	def __str__(self):return str(self.value)
	def __repr__(self):return str(self.value)
Number.null=Number(0)
Number.false=Number(0)
Number.true=Number(1)
Number.math_PI=Number(math.pi)
Number.e=Number(math.e)
Number.inf=Number(math.inf)
Number.nan=Number(math.nan)
Number.tau=Number(math.tau)
class String(Value):
	def __init__(self,value):super().__init__();self.value=value
	def added_to(self,other):
		if isinstance(other,String):return String(self.value+other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def multed_by(self,other):
		if isinstance(other,Number):return String(self.value*other.value).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def dived_by(self,other):
		if isinstance(other,Number):
			try:return String(self.value[other.value]).set_context(self.context),_A
			except:return _A,RTError(other.pos_start,other.pos_end,'Element at this index could not be retrieved from string because index is out of bounds',self.context)
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_eq(self,other):
		if isinstance(other,String):return Number(int(self.value==other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def get_comparison_ne(self,other):
		if isinstance(other,String):return Number(int(self.value!=other.value)).set_context(self.context),_A
		else:return _A,Value.illegal_operation(self,other)
	def is_true(self):return len(self.value)>0
	def copy(self):copy=String(self.value);copy.set_pos(self.pos_start,self.pos_end);copy.set_context(self.context);return copy
	def __str__(self):return self.value
	def __repr__(self):return f'"{self.value}"'
class List(Value):
	def __init__(self,elements):super().__init__();self.elements=elements
	def added_to(self,other):new_list=self.copy();new_list.elements.append(other);return new_list,_A
	def subbed_by(self,other):
		if isinstance(other,Number):
			new_list=self.copy()
			try:new_list.elements.pop(other.value);return new_list,_A
			except:return _A,RTError(other.pos_start,other.pos_end,_i,self.context)
		else:return _A,Value.illegal_operation(self,other)
	def multed_by(self,other):
		if isinstance(other,List):new_list=self.copy();new_list.elements.extend(other.elements);return new_list,_A
		else:return _A,Value.illegal_operation(self,other)
	def dived_by(self,other):
		if isinstance(other,Number):
			try:return self.elements[other.value],_A
			except:return _A,RTError(other.pos_start,other.pos_end,'Element at this index could not be retrieved from list because index is out of bounds',self.context)
		else:return _A,Value.illegal_operation(self,other)
	def copy(self):copy=List(self.elements);copy.set_pos(self.pos_start,self.pos_end);copy.set_context(self.context);return copy
	def __str__(self):return ', '.join([str(x)for x in self.elements])
	def __repr__(self):return f"[{', '.join([repr(x)for x in self.elements])}]"
class BaseFunction(Value):
	def __init__(self,name):super().__init__();self.name=name or'<anonymous>'
	def generate_new_context(self):new_context=Context(self.name,self.context,self.pos_start);new_context.symbol_table=SymbolTable(new_context.parent.symbol_table);return new_context
	def check_args(self,arg_names,args):
		res=RTResult()
		if len(args)>len(arg_names):return res.failure(RTError(self.pos_start,self.pos_end,f"{len(args)-len(arg_names)} too many args passed into {self}",self.context))
		if len(args)<len(arg_names):return res.failure(RTError(self.pos_start,self.pos_end,f"{len(arg_names)-len(args)} too few args passed into {self}",self.context))
		return res.success(_A)
	def populate_args(self,arg_names,args,exec_ctx):
		for i in range(len(args)):arg_name=arg_names[i];arg_value=args[i];arg_value.set_context(exec_ctx);exec_ctx.symbol_table.set(arg_name,arg_value)
	def check_and_populate_args(self,arg_names,args,exec_ctx):
		res=RTResult();res.register(self.check_args(arg_names,args))
		if res.should_return():return res
		self.populate_args(arg_names,args,exec_ctx);return res.success(_A)
class Function(BaseFunction):
	def __init__(self,name,body_node,arg_names,should_auto_return):super().__init__(name);self.body_node=body_node;self.arg_names=arg_names;self.should_auto_return=should_auto_return
	def execute(self,args):
		res=RTResult();interpreter=Interpreter();exec_ctx=self.generate_new_context();res.register(self.check_and_populate_args(self.arg_names,args,exec_ctx))
		if res.should_return():return res
		value=res.register(interpreter.visit(self.body_node,exec_ctx))
		if res.should_return()and res.func_return_value==_A:return res
		ret_value=(value if self.should_auto_return else _A)or res.func_return_value or Number.null;return res.success(ret_value)
	def copy(self):copy=Function(self.name,self.body_node,self.arg_names,self.should_auto_return);copy.set_context(self.context);copy.set_pos(self.pos_start,self.pos_end);return copy
	def __repr__(self):return f"<function {self.name}>"
class bif(BaseFunction):
	def __init__(self,name):super().__init__(name)
	def execute(self,args):
		res=RTResult();exec_ctx=self.generate_new_context();method_name=f"execute_{self.name}";method=getattr(self,method_name,self.no_visit_method);res.register(self.check_and_populate_args(method.arg_names,args,exec_ctx))
		if res.should_return():return res
		return_value=res.register(method(exec_ctx))
		if res.should_return():return res
		return res.success(return_value)
	def no_visit_method(self,node,context):raise Exception(f"No execute_{self.name} method defined")
	def copy(self):copy=bif(self.name);copy.set_context(self.context);copy.set_pos(self.pos_start,self.pos_end);return copy
	def __repr__(self):return f"<built-in function {self.name}>"
	def execute_print(self,exec_ctx):print(str(exec_ctx.symbol_table.get(_C)));return RTResult().success(Number.null)
	execute_print.arg_names=[_C]
	def execute_python(self,exec_ctx):
		code=exec_ctx.symbol_table.get(_C)
		try:result=compile(code.value.replace('\\n',_G).replace('\\t',_P).replace('\\r','\r'),'<eval>',_j);result=exec(result,execGlobals,execLocals);text=str(result)
		except Exception as e:return RTResult().failure(RTError(self.pos_start,self.pos_end,f"Python error: {str(e)}",exec_ctx))
		return RTResult().success(String(text))
	execute_python.arg_names=[_C]
	def execute_print_ret(self,exec_ctx):return RTResult().success(String(str(exec_ctx.symbol_table.get(_C))))
	execute_print_ret.arg_names=[_C]
	def execute_input(self,exec_ctx):text=input();return RTResult().success(String(text))
	execute_input.arg_names=[]
	def execute_read_file(self,exec_ctx):
		file_name=exec_ctx.symbol_table.get(_C)
		try:
			with open(file_name.value)as f:text=f.read()
		except Exception as e:return RTResult().failure(RTError(self.pos_start,self.pos_end,f"Failed to open file {file_name.value}",exec_ctx))
		return RTResult().success(String(text))
	execute_read_file.arg_names=[_C]
	def execute_input_int(self,exec_ctx):
		while _E:
			text=input()
			try:number=int(text);break
			except ValueError:print(f"'{text}' must be an integer. Try again!")
		return RTResult().success(Number(number))
	execute_input_int.arg_names=[]
	def execute_clear(self,exec_ctx):os.system(_Y if os.name=='nt'else _Y);return RTResult().success(Number.null)
	execute_clear.arg_names=[]
	def execute_is_number(self,exec_ctx):is_number=isinstance(exec_ctx.symbol_table.get(_C),Number);return RTResult().success(Number.true if is_number else Number.false)
	execute_is_number.arg_names=[_C]
	def execute_is_string(self,exec_ctx):is_number=isinstance(exec_ctx.symbol_table.get(_C),String);return RTResult().success(Number.true if is_number else Number.false)
	execute_is_string.arg_names=[_C]
	def execute_is_list(self,exec_ctx):is_number=isinstance(exec_ctx.symbol_table.get(_C),List);return RTResult().success(Number.true if is_number else Number.false)
	execute_is_list.arg_names=[_C]
	def execute_python_import(self,exec_ctx):
		code=exec_ctx.symbol_table.get(_C)
		try:globals()[code.value]=import_module(code.value)
		except Exception as e:return RTResult().failure(RTError(self.pos_start,self.pos_end,f"Python error: {str(e)}",exec_ctx))
		return RTResult().success(Number.null)
	execute_python_import.arg_names=[_C]
	def execute_is_function(self,exec_ctx):is_number=isinstance(exec_ctx.symbol_table.get(_C),BaseFunction);return RTResult().success(Number.true if is_number else Number.false)
	execute_is_function.arg_names=[_C]
	def execute_append(self,exec_ctx):
		list_=exec_ctx.symbol_table.get(_I);value=exec_ctx.symbol_table.get(_C)
		if not isinstance(list_,List):return RTResult().failure(RTError(self.pos_start,self.pos_end,_Z,exec_ctx))
		list_.elements.append(value);return RTResult().success(Number.null)
	execute_append.arg_names=[_I,_C]
	def execute_pop(self,exec_ctx):
		list_=exec_ctx.symbol_table.get(_I);index=exec_ctx.symbol_table.get(_k)
		if not isinstance(list_,List):return RTResult().failure(RTError(self.pos_start,self.pos_end,_Z,exec_ctx))
		if not isinstance(index,Number):return RTResult().failure(RTError(self.pos_start,self.pos_end,'Second argument must be number',exec_ctx))
		try:element=list_.elements.pop(index.value)
		except:return RTResult().failure(RTError(self.pos_start,self.pos_end,_i,exec_ctx))
		return RTResult().success(element)
	execute_pop.arg_names=[_I,_k]
	def execute_extend(self,exec_ctx):
		listA=exec_ctx.symbol_table.get(_l);listB=exec_ctx.symbol_table.get(_m)
		if not isinstance(listA,List):return RTResult().failure(RTError(self.pos_start,self.pos_end,_Z,exec_ctx))
		if not isinstance(listB,List):return RTResult().failure(RTError(self.pos_start,self.pos_end,'Second argument must be list',exec_ctx))
		listA.elements.extend(listB.elements);return RTResult().success(Number.null)
	execute_extend.arg_names=[_l,_m]
	def execute_len(self,exec_ctx):
		list_=exec_ctx.symbol_table.get(_I)
		if not isinstance(list_,List)and not isinstance(list_,String):return RTResult().failure(RTError(self.pos_start,self.pos_end,'Argument must be list or string',exec_ctx))
		if isinstance(list_,List):return RTResult().success(Number(len(list_.elements)))
		return RTResult().success(Number(len(list_.value)))
	execute_len.arg_names=[_I]
	def execute_run(self,exec_ctx):
		fn=exec_ctx.symbol_table.get(_J)
		if not isinstance(fn,String):return RTResult().failure(RTError(self.pos_start,self.pos_end,'Second argument must be string',exec_ctx))
		fn=fn.value
		try:
			with open(fn,'r')as f:script=f.read()
		except Exception as e:return RTResult().failure(RTError(self.pos_start,self.pos_end,f'Failed to load script "{fn}"\n'+str(e),exec_ctx))
		_,error=run(fn,script)
		if error:return RTResult().failure(RTError(self.pos_start,self.pos_end,f'Failed to finish executing script "{fn}"\n'+error.as_string(),exec_ctx))
		return RTResult().success(Number.null)
	execute_run.arg_names=[_J]
	def execute_open_window(self,exec_ctx):createWindow(str(exec_ctx.symbol_table.get(_n)),str(exec_ctx.symbol_table.get(_o)));return RTResult().success(Number.null)
	execute_open_window.arg_names=[_n,_o]
	def execute_close_window(self,exec_ctx):closeWindow();return RTResult().success(Number.null)
	execute_close_window.arg_names=[]
	def execute_window_width(self,exec_ctx):return RTResult().success(Number(getWindowWidth()))
	execute_window_width.arg_names=[]
	def execute_window_height(self,exec_ctx):return RTResult().success(Number(getWindowHeight()))
	execute_window_height.arg_names=[]
	def execute_resize_window(self,exec_ctx):resizeWindow(exec_ctx.symbol_table.get(_p).value,exec_ctx.symbol_table.get(_q).value);return RTResult().success(Number.null)
	execute_resize_window.arg_names=[_q,_p]
	def execute_clear_window(self,exec_ctx):clearWindow();return RTResult().success(Number.null)
	execute_clear_window.arg_names=[]
	def execute_create_button(self,exec_ctx):addButton(str(exec_ctx.symbol_table.get(_N)),exec_ctx.symbol_table.get(_B).value,exec_ctx.symbol_table.get(_D).value,exec_ctx.symbol_table.get(_r).value);return RTResult().success(Number.null)
	execute_create_button.arg_names=[_N,_B,_D,_r]
	def execute_create_text(self,exec_ctx):addText(str(exec_ctx.symbol_table.get(_N)),exec_ctx.symbol_table.get(_B).value,exec_ctx.symbol_table.get(_D).value);return RTResult().success(Number.null)
	execute_create_text.arg_names=[_N,_B,_D]
	def execute_math_acos(self,exec_ctx):return RTResult().success(Number(math.acos(exec_ctx.symbol_table.get(_B).value)))
	execute_math_acos.arg_names=[_B]
	def execute_math_acosh(self,exec_ctx):return RTResult().success(Number(math.acosh(exec_ctx.symbol_table.get(_B).value)))
	execute_math_acosh.arg_names=[_B]
	def execute_math_asin(self,exec_ctx):return RTResult().success(Number(math.asin(exec_ctx.symbol_table.get(_B).value)))
	execute_math_asin.arg_names=[_B]
	def execute_math_asinh(self,exec_ctx):return RTResult().success(Number(math.asinh(exec_ctx.symbol_table.get(_B).value)))
	execute_math_asinh.arg_names=[_B]
	def execute_math_atan(self,exec_ctx):return RTResult().success(Number(math.atan(exec_ctx.symbol_table.get(_B).value)))
	execute_math_atan.arg_names=[_B]
	def execute_math_atanh(self,exec_ctx):return RTResult().success(Number(math.atanh(exec_ctx.symbol_table.get(_B).value)))
	execute_math_atanh.arg_names=[_B]
	def execute_math_atan2(self,exec_ctx):return RTResult().success(Number(math.atan2(exec_ctx.symbol_table.get(_D).value,exec_ctx.symbol_table.get(_B).value)))
	execute_math_atan2.arg_names=[_D,_B]
	def execute_math_cbrt(self,exec_ctx):return RTResult().success(Number(math.cbrt(exec_ctx.symbol_table.get(_B).value)))
	execute_math_cbrt.arg_names=[_B]
	def execute_math_ceil(self,exec_ctx):return RTResult().success(Number(math.ceil(exec_ctx.symbol_table.get(_B).value)))
	execute_math_ceil.arg_names=[_B]
	def execute_math_cos(self,exec_ctx):return RTResult().success(Number(math.cos(exec_ctx.symbol_table.get(_B).value)))
	execute_math_cos.arg_names=[_B]
	def execute_math_cosh(self,exec_ctx):return RTResult().success(Number(math.cosh(exec_ctx.symbol_table.get(_B).value)))
	execute_math_cosh.arg_names=[_B]
	def execute_math_degrees(self,exec_ctx):return RTResult().success(Number(math.degrees(exec_ctx.symbol_table.get(_B).value)))
	execute_math_degrees.arg_names=[_B]
	def execute_math_erf(self,exec_ctx):return RTResult().success(Number(math.erf(exec_ctx.symbol_table.get(_B).value)))
	execute_math_erf.arg_names=[_B]
	def execute_math_erfc(self,exec_ctx):return RTResult().success(Number(math.erfc(exec_ctx.symbol_table.get(_B).value)))
	execute_math_erfc.arg_names=[_B]
	def execute_math_exp(self,exec_ctx):return RTResult().success(Number(math.exp(exec_ctx.symbol_table.get(_B).value)))
	execute_math_exp.arg_names=[_B]
	def execute_math_expm1(self,exec_ctx):return RTResult().success(Number(math.expm1(exec_ctx.symbol_table.get(_B).value)))
	execute_math_expm1.arg_names=[_B]
	def execute_math_floor(self,exec_ctx):return RTResult().success(Number(math.floor(exec_ctx.symbol_table.get(_B).value)))
	execute_math_floor.arg_names=[_B]
	def execute_math_gamma(self,exec_ctx):return RTResult().success(Number(math.gamma(exec_ctx.symbol_table.get(_B).value)))
	execute_math_gamma.arg_names=[_B]
	def execute_math_lgamma(self,exec_ctx):return RTResult().success(Number(math.lgamma(exec_ctx.symbol_table.get(_B).value)))
	execute_math_lgamma.arg_names=[_B]
	def execute_math_log(self,exec_ctx):return RTResult().success(Number(math.log(exec_ctx.symbol_table.get(_B).value)))
	execute_math_log.arg_names=[_B]
	def execute_math_log10(self,exec_ctx):return RTResult().success(Number(math.log10(exec_ctx.symbol_table.get(_B).value)))
	execute_math_log10.arg_names=[_B]
	def execute_math_log1p(self,exec_ctx):return RTResult().success(Number(math.log1p(exec_ctx.symbol_table.get(_B).value)))
	execute_math_log1p.arg_names=[_B]
	def execute_math_log2(self,exec_ctx):return RTResult().success(Number(math.log2(exec_ctx.symbol_table.get(_B).value)))
	execute_math_log2.arg_names=[_B]
	def execute_math_radians(self,exec_ctx):return RTResult().success(Number(math.radians(exec_ctx.symbol_table.get(_B).value)))
	execute_math_radians.arg_names=[_B]
	def execute_math_sin(self,exec_ctx):return RTResult().success(Number(math.sin(exec_ctx.symbol_table.get(_B).value)))
	execute_math_sin.arg_names=[_B]
	def execute_math_sinh(self,exec_ctx):return RTResult().success(Number(math.sinh(exec_ctx.symbol_table.get(_B).value)))
	execute_math_sinh.arg_names=[_B]
	def execute_math_sqrt(self,exec_ctx):return RTResult().success(Number(math.sqrt(exec_ctx.symbol_table.get(_B).value)))
	execute_math_sqrt.arg_names=[_B]
	def execute_math_tan(self,exec_ctx):return RTResult().success(Number(math.tan(exec_ctx.symbol_table.get(_B).value)))
	execute_math_tan.arg_names=[_B]
	def execute_math_tanh(self,exec_ctx):return RTResult().success(Number(math.tanh(exec_ctx.symbol_table.get(_B).value)))
	execute_math_tanh.arg_names=[_B]
	def execute_math_trunc(self,exec_ctx):return RTResult().success(Number(math.trunc(exec_ctx.symbol_table.get(_B).value)))
	execute_math_trunc.arg_names=[_B]
	def execute_str_len(self,exec_ctx):return RTResult().success(Number(len(exec_ctx.symbol_table.get(_B).value)))
	execute_str_len.arg_names=[_B]
	def execute_str_upper(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.upper()))
	execute_str_upper.arg_names=[_B]
	def execute_str_lower(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.lower()))
	execute_str_lower.arg_names=[_B]
	def execute_str_strip(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.strip()))
	execute_str_strip.arg_names=[_B]
	def execute_str_lstrip(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.lstrip()))
	execute_str_lstrip.arg_names=[_B]
	def execute_str_rstrip(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.rstrip()))
	execute_str_rstrip.arg_names=[_B]
	def execute_str_join(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.join(exec_ctx.symbol_table.get(_D).value)))
	execute_str_join.arg_names=[_B,_D]
	def execute_str_split(self,exec_ctx):return RTResult().success(List([String(s)for s in exec_ctx.symbol_table.get(_B).value.split(exec_ctx.symbol_table.get(_D).value)]))
	execute_str_split.arg_names=[_B,_D]
	def execute_str_replace(self,exec_ctx):return RTResult().success(String(exec_ctx.symbol_table.get(_B).value.replace(exec_ctx.symbol_table.get(_D).value,exec_ctx.symbol_table.get('z').value)))
	execute_str_replace.arg_names=[_B,_D,'z']
	def execute_str_startswith(self,exec_ctx):return RTResult().success(Number(int(exec_ctx.symbol_table.get(_B).value.startswith(exec_ctx.symbol_table.get(_D).value))==_E))
	execute_str_startswith.arg_names=[_B,_D]
	def execute_str_endswith(self,exec_ctx):return RTResult().success(Number(int(exec_ctx.symbol_table.get(_B).value.endswith(exec_ctx.symbol_table.get(_D).value==_E))))
	execute_str_endswith.arg_names=[_B,_D]
	def execute_writefile(self,exec_ctx):
		file_name=exec_ctx.symbol_table.get(_s).value;content=exec_ctx.symbol_table.get(_t).value
		with open(file_name,'w')as f:f.write(content);f.close()
		return RTResult().success(Number(1))
	execute_writefile.arg_names=[_s,_t]
	def execute_hang(self,exec_ctx):hang();return RTResult().success(Number(1))
	execute_hang.arg_names=[]
	def execute_exit(self,exec_ctx):sys.exit(0)
	execute_exit.arg_names=[]
	def execute_import(self,exec_ctx):
		fn=exec_ctx.symbol_table.get(_J)
		if not isinstance(fn,String):return RTResult().failure(RTError(self.pos_start,self.pos_end,'Argument must be string',exec_ctx))
		fn=fn.value;pth=os.path.dirname(__file__);pth=os.path.join(pth,_u)
		try:
			with open(os.path.join(pth,fn,fn+_a),'r')as f:script=f.read()
		except Exception as e:return RTResult().failure(RTError(self.pos_start,self.pos_end,f'Failed to load script "{fn}"\n'+str(e),exec_ctx))
		try:
			with open(os.path.join(pth,fn,'init.py'),'r')as f:script2=f.read()
		except Exception as e:return RTResult().failure(RTError(self.pos_start,self.pos_end,f'Failed to load script "init.py"\n'+str(e),exec_ctx))
		exec(compile(script2,'<init.py> for module '+fn,_j),execGlobals,execLocals);_,error=run(fn,script)
		if error:return RTResult().failure(RTError(self.pos_start,self.pos_end,f'Failed to finish executing script "{fn}"\n'+error.as_string(),exec_ctx))
		return RTResult().success(Number.null)
	execute_import.arg_names=[_J]
	def execute_eval(self,exec_ctx):
		result,error=run(exec_ctx.symbol_table.get(_J))
		if error:return RTResult().failure(RTError(self.pos_start,self.pos_end,f"Script threw error whilst executing:\n"+error.as_string(),exec_ctx))
		return RTResult().success(Number.null)
	execute_eval.arg_names=[_J]
	def execute_mouse_click(self,exec_ctx):pyautogui.click();return RTResult().success(Number.null)
	execute_mouse_click.arg_names=[]
	def execute_mouse_click_png(self,exec_ctx):pyautogui.click(exec_ctx.symbol_table.get(_v).value);return RTResult().success(Number.null)
	execute_mouse_click_png.arg_names=[_v]
	def execute_mouse_move(self,exec_ctx):pyautogui.moveTo(exec_ctx.symbol_table.get(_B).value,exec_ctx.symbol_table.get(_D).value);return RTResult().success(Number.null)
	execute_mouse_move.arg_names=[_B,_D]
	def execute_mouse_scroll(self,exec_ctx):pyautogui.scroll(exec_ctx.symbol_table.get(_B).value);return RTResult().success(Number.null)
	execute_mouse_scroll.arg_names=[_B]
	def execute_key_type(self,exec_ctx):pyautogui.typewrite(exec_ctx.symbol_table.get(_O).value);return RTResult().success(Number.null)
	execute_key_type.arg_names=[_O]
	def execute_key_press(self,exec_ctx):pyautogui.press(exec_ctx.symbol_table.get(_O).value);return RTResult().success(Number.null)
	execute_key_press.arg_names=[_O]
	def execute_delay(self,exec_ctx):time.sleep(exec_ctx.symbol_table.get(_w).value);return RTResult().success(Number.null)
	execute_delay.arg_names=[_w]
bif.print=bif(_x)
bif.print_ret=bif(_y)
bif.input=bif(_z)
bif.input_int=bif(_A0)
bif.clear=bif(_A1)
bif.is_number=bif('is_number')
bif.is_string=bif('is_string')
bif.is_list=bif(_A2)
bif.is_function=bif('is_function')
bif.append=bif(_A3)
bif.pop=bif('pop')
bif.hang=bif('hang')
bif.extend=bif(_A4)
bif.len=bif('len')
bif.run=bif('run')
bif.python=bif(_A5)
bif.python_import=bif('python_import')
bif.read_file=bif('read_file')
bif.open_window=bif('open_window')
bif.close_window=bif('close_window')
bif.window_width=bif(_A6)
bif.window_height=bif(_A7)
bif.resize_window=bif('resize_window')
bif.clear_window=bif('clear_window')
bif.create_button=bif('create_button')
bif.create_text=bif('create_text')
bif.math_acos=bif(_A8)
bif.math_acosh=bif(_A9)
bif.math_asin=bif(_AA)
bif.math_asinh=bif(_AB)
bif.math_atan=bif(_AC)
bif.math_atanh=bif(_AD)
bif.math_atan2=bif(_AE)
bif.math_cbrt=bif(_AF)
bif.math_ceil=bif(_AG)
bif.math_cos=bif(_AH)
bif.math_cosh=bif(_AI)
bif.math_degrees=bif(_AJ)
bif.math_erf=bif(_AK)
bif.math_erfc=bif(_AL)
bif.math_exp=bif(_AM)
bif.math_expm1=bif(_AN)
bif.math_fabs=bif(_AO)
bif.math_factorial=bif(_AP)
bif.math_floor=bif(_AQ)
bif.math_gamma=bif(_AR)
bif.math_lgamma=bif(_AS)
bif.math_log=bif(_AT)
bif.math_log10=bif(_AU)
bif.math_log1p=bif(_AV)
bif.math_log2=bif(_AW)
bif.math_modf=bif(_AX)
bif.math_pow=bif(_AY)
bif.math_radians=bif(_AZ)
bif.math_sin=bif(_Aa)
bif.math_sinh=bif(_Ab)
bif.math_sqrt=bif(_Ac)
bif.math_tan=bif(_Ad)
bif.math_tanh=bif(_Ae)
bif.math_trunc=bif(_Af)
bif.str_len=bif(_Ag)
bif.str_lower=bif(_Ah)
bif.str_upper=bif(_Ai)
bif.str_split=bif(_Aj)
bif.str_strip=bif(_Ak)
bif.str_lstrip=bif(_Al)
bif.str_rstrip=bif(_Am)
bif.str_join=bif(_An)
bif.str_replace=bif(_Ao)
bif.str_startswith=bif(_Ap)
bif.str_endswith=bif(_Aq)
bif.writefile=bif(_Ar)
bif.exit=bif('exit')
bif.import_=bif(_As)
bif.eval=bif('eval')
bif.mouse_click=bif(_At)
bif.mouse_click_png=bif(_Au)
bif.mouse_move=bif(_Av)
bif.mouse_scroll=bif(_Aw)
bif.key_type=bif(_Ax)
bif.key_press=bif(_Ay)
bif.delay=bif(_Az)
class Context:
	def __init__(self,display_name,parent=_A,parent_entry_pos=_A):self.display_name=display_name;self.parent=parent;self.parent_entry_pos=parent_entry_pos;self.symbol_table=_A
class SymbolTable:
	def __init__(self,parent=_A):self.symbols={};self.parent=parent
	def get(self,name):
		value=self.symbols.get(name,_A)
		if value==_A and self.parent:return self.parent.get(name)
		return value
	def set(self,name,value):self.symbols[name]=value
	def remove(self,name):del self.symbols[name]
class Interpreter:
	def visit(self,node,context):method_name=f"visit_{type(node).__name__}";method=getattr(self,method_name,self.no_visit_method);return method(node,context)
	def no_visit_method(self,node,context):raise Exception(f"No visit_{type(node).__name__} method defined")
	def visit_NumberNode(self,node,context):return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start,node.pos_end))
	def visit_StringNode(self,node,context):return RTResult().success(String(node.tok.value).set_context(context).set_pos(node.pos_start,node.pos_end))
	def visit_ListNode(self,node,context):
		res=RTResult();elements=[]
		for element_node in node.element_nodes:
			elements.append(res.register(self.visit(element_node,context)))
			if res.should_return():return res
		return res.success(List(elements).set_context(context).set_pos(node.pos_start,node.pos_end))
	def visit_VarAccessNode(self,node,context):
		res=RTResult();var_name=node.var_name_tok.value;value=context.symbol_table.get(var_name)
		if not value:return res.failure(RTError(node.pos_start,node.pos_end,f"'{var_name}' is not defined",context))
		value=value.copy().set_pos(node.pos_start,node.pos_end).set_context(context);return res.success(value)
	def visit_VarAssignNode(self,node,context):
		res=RTResult();var_name=node.var_name_tok.value;value=res.register(self.visit(node.value_node,context))
		if res.should_return():return res
		context.symbol_table.set(var_name,value);return res.success(value)
	def visit_BinOpNode(self,node,context):
		res=RTResult();left=res.register(self.visit(node.left_node,context))
		if res.should_return():return res
		right=res.register(self.visit(node.right_node,context))
		if res.should_return():return res
		if node.op_tok.type==TT_PLUS:result,error=left.added_to(right)
		elif node.op_tok.type==TT_MINUS:result,error=left.subbed_by(right)
		elif node.op_tok.type==TT_MUL:result,error=left.multed_by(right)
		elif node.op_tok.type==TT_DIV:result,error=left.dived_by(right)
		elif node.op_tok.type==TT_POW:result,error=left.powed_by(right)
		elif node.op_tok.type==TT_EE:result,error=left.get_comparison_eq(right)
		elif node.op_tok.type==TT_NE:result,error=left.get_comparison_ne(right)
		elif node.op_tok.type==TT_LT:result,error=left.get_comparison_lt(right)
		elif node.op_tok.type==TT_GT:result,error=left.get_comparison_gt(right)
		elif node.op_tok.type==TT_LTE:result,error=left.get_comparison_lte(right)
		elif node.op_tok.type==TT_GTE:result,error=left.get_comparison_gte(right)
		elif node.op_tok.matches(TT_KEYWORD,_Q):result,error=left.anded_by(right)
		elif node.op_tok.matches(TT_KEYWORD,_R):result,error=left.ored_by(right)
		if error:return res.failure(error)
		else:return res.success(result.set_pos(node.pos_start,node.pos_end))
	def visit_UnaryOpNode(self,node,context):
		res=RTResult();number=res.register(self.visit(node.node,context))
		if res.should_return():return res
		error=_A
		if node.op_tok.type==TT_MINUS:number,error=number.multed_by(Number(-1))
		elif node.op_tok.matches(TT_KEYWORD,_S):number,error=number.notted()
		if error:return res.failure(error)
		else:return res.success(number.set_pos(node.pos_start,node.pos_end))
	def visit_IfNode(self,node,context):
		res=RTResult()
		for (condition,expr,should_return_null) in node.cases:
			condition_value=res.register(self.visit(condition,context))
			if res.should_return():return res
			if condition_value.is_true():
				expr_value=res.register(self.visit(expr,context))
				if res.should_return():return res
				return res.success(Number.null if should_return_null else expr_value)
		if node.else_case:
			expr,should_return_null=node.else_case;expr_value=res.register(self.visit(expr,context))
			if res.should_return():return res
			return res.success(Number.null if should_return_null else expr_value)
		return res.success(Number.null)
	def visit_ForNode(self,node,context):
		res=RTResult();elements=[];start_value=res.register(self.visit(node.start_value_node,context))
		if res.should_return():return res
		end_value=res.register(self.visit(node.end_value_node,context))
		if res.should_return():return res
		if node.step_value_node:
			step_value=res.register(self.visit(node.step_value_node,context))
			if res.should_return():return res
		else:step_value=Number(1)
		i=start_value.value
		if step_value.value>=0:condition=lambda:i<end_value.value
		else:condition=lambda:i>end_value.value
		while condition():
			context.symbol_table.set(node.var_name_tok.value,Number(i));i+=step_value.value;value=res.register(self.visit(node.body_node,context))
			if res.should_return()and res.loop_should_continue==_F and res.loop_should_break==_F:return res
			if res.loop_should_continue:continue
			if res.loop_should_break:break
			elements.append(value)
		return res.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start,node.pos_end))
	def visit_WhileNode(self,node,context):
		res=RTResult();elements=[]
		while _E:
			condition=res.register(self.visit(node.condition_node,context))
			if res.should_return():return res
			if not condition.is_true():break
			value=res.register(self.visit(node.body_node,context))
			if res.should_return()and res.loop_should_continue==_F and res.loop_should_break==_F:return res
			if res.loop_should_continue:continue
			if res.loop_should_break:break
			elements.append(value)
		return res.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start,node.pos_end))
	def visit_FuncDefNode(self,node,context):
		res=RTResult();func_name=node.var_name_tok.value if node.var_name_tok else _A;body_node=node.body_node;arg_names=[arg_name.value for arg_name in node.arg_name_toks];func_value=Function(func_name,body_node,arg_names,node.should_auto_return).set_context(context).set_pos(node.pos_start,node.pos_end)
		if node.var_name_tok:context.symbol_table.set(func_name,func_value)
		return res.success(func_value)
	def visit_CallNode(self,node,context):
		res=RTResult();args=[];value_to_call=res.register(self.visit(node.node_to_call,context))
		if res.should_return():return res
		value_to_call=value_to_call.copy().set_pos(node.pos_start,node.pos_end)
		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node,context)))
			if res.should_return():return res
		return_value=res.register(value_to_call.execute(args))
		if res.should_return():return res
		return_value=return_value.copy().set_pos(node.pos_start,node.pos_end).set_context(context);return res.success(return_value)
	def visit_ReturnNode(self,node,context):
		res=RTResult()
		if node.node_to_return:
			value=res.register(self.visit(node.node_to_return,context))
			if res.should_return():return res
		else:value=Number.null
		return res.success_return(value)
	def visit_ContinueNode(self,node,context):return RTResult().success_continue()
	def visit_BreakNode(self,node,context):return RTResult().success_break()
gst=SymbolTable()
gst.set('Null',Number.null)
gst.set('false',Number.false)
gst.set('true',Number.true)
gst.set('math_pi',Number.math_PI)
gst.set(_x,bif.print)
gst.set(_y,bif.print_ret)
gst.set(_z,bif.input)
gst.set(_A0,bif.input_int)
gst.set(_A1,bif.clear)
gst.set(_Y,bif.clear)
gst.set('is_num',bif.is_number)
gst.set('is_str',bif.is_string)
gst.set(_A2,bif.is_list)
gst.set('is_func',bif.is_function)
gst.set(_A3,bif.append)
gst.set('pop',bif.pop)
gst.set(_A4,bif.extend)
gst.set('len',bif.len)
gst.set('run',bif.run)
gst.set('hang',bif.hang)
gst.set('exit',bif.exit)
gst.set('eval',bif.eval)
gst.set(_A5,bif.python)
gst.set('py',bif.python)
gst.set('py_import',bif.python_import)
gst.set('readfile',bif.read_file)
gst.set(_Ar,bif.writefile)
gst.set('openwindow',bif.open_window)
gst.set('closewindow',bif.close_window)
gst.set(_A6,bif.window_width)
gst.set(_A7,bif.window_height)
gst.set('window_resize',bif.resize_window)
gst.set('window_clear',bif.clear_window)
gst.set('window_create_button',bif.create_button)
gst.set('window_create_text',bif.create_text)
gst.set('math_e',Number.e)
gst.set('math_inf',Number.inf)
gst.set('math_nan',Number.nan)
gst.set('math_tau',Number.tau)
gst.set(_A8,bif.math_acos)
gst.set(_A9,bif.math_acosh)
gst.set(_AA,bif.math_asin)
gst.set(_AB,bif.math_asinh)
gst.set(_AC,bif.math_atan)
gst.set(_AD,bif.math_atanh)
gst.set(_AE,bif.math_atan2)
gst.set(_AF,bif.math_cbrt)
gst.set(_AG,bif.math_ceil)
gst.set(_AH,bif.math_cos)
gst.set(_AI,bif.math_cosh)
gst.set(_AJ,bif.math_degrees)
gst.set(_AK,bif.math_erf)
gst.set(_AL,bif.math_erfc)
gst.set(_AM,bif.math_exp)
gst.set(_AN,bif.math_expm1)
gst.set(_AO,bif.math_fabs)
gst.set(_AP,bif.math_factorial)
gst.set(_AQ,bif.math_floor)
gst.set(_AR,bif.math_gamma)
gst.set(_AS,bif.math_lgamma)
gst.set(_AT,bif.math_log)
gst.set(_AU,bif.math_log10)
gst.set(_AV,bif.math_log1p)
gst.set(_AW,bif.math_log2)
gst.set(_AX,bif.math_modf)
gst.set(_AY,bif.math_pow)
gst.set(_AZ,bif.math_radians)
gst.set(_Aa,bif.math_sin)
gst.set(_Ab,bif.math_sinh)
gst.set(_Ac,bif.math_sqrt)
gst.set(_Ad,bif.math_tan)
gst.set(_Ae,bif.math_tanh)
gst.set(_Af,bif.math_trunc)
gst.set(_Ag,bif.str_len)
gst.set(_Ah,bif.str_lower)
gst.set(_Ai,bif.str_upper)
gst.set(_Aj,bif.str_split)
gst.set(_An,bif.str_join)
gst.set(_Ak,bif.str_strip)
gst.set(_Al,bif.str_lstrip)
gst.set(_Am,bif.str_rstrip)
gst.set(_Ap,bif.str_startswith)
gst.set(_Aq,bif.str_endswith)
gst.set(_Ao,bif.str_replace)
gst.set(_As,bif.import_)
gst.set(_At,bif.mouse_click)
gst.set(_Au,bif.mouse_click_png)
gst.set(_Av,bif.mouse_move)
gst.set(_Aw,bif.mouse_scroll)
gst.set(_Ax,bif.key_type)
gst.set(_Ay,bif.key_press)
gst.set(_Az,bif.delay)
def run(fn,text):
	lexer=Lexer(fn,text);tokens,error=lexer.make_tokens()
	if error:return _A,error
	parser=Parser(tokens);ast=parser.parse()
	if ast.error:return _A,ast.error
	interpreter=Interpreter();context=Context('<program>');context.symbol_table=gst;result=interpreter.visit(ast.node,context);return result.value,result.error
def installPkg(pkg):
	C='setup.py';B='w+';A='utf-8';pkg_path=os.path.join(os.path.dirname(__file__),_u,pkg)
	if os.path.exists(pkg_path):print("Package '%s' already installed."%pkg);return 0
	else:
		os.mkdir(pkg_path);cloud_url='https://raw.githubusercontent.com/HENRYMARTIN5/SolutionPackages/main/'+pkg+'/';print("Downloading package '%s'..."%pkg);print('Fetching dependencies...');dependencies=[]
		with urllib.request.urlopen(cloud_url+'deps')as f:
			if f.code==200:dependencies=f.read().decode(A).splitlines()
			else:print("Package '%s' does not exist."%pkg);return
		for dependency in dependencies:
			if dependency!='':installPkg(dependency)
		print("Downloading '%s.ph'..."%pkg)
		with urllib.request.urlopen(cloud_url+pkg+_a)as f:
			ph=f.read().decode(A)
			with open(os.path.join(pkg_path,pkg+_a),B)as f:f.write(ph)
		print('Downloading setup files...')
		with urllib.request.urlopen(cloud_url+C)as f:
			setup_py=f.read().decode(A)
			with open(os.path.join(pkg_path,C),B)as f:f.write(setup_py)
			print("Installing package '%s'..."%pkg);eval(setup_py)
		print("Package '%s' installed!"%pkg);return 1
def main():
	try:
		if sys.argv[1]:
			if sys.argv[1]=='install':
				if len(sys.argv)>2:installPkg(sys.argv[2]);return
				else:print('Please specify a package name.');return
			result,error=run(sys.argv[1],'run("'+sys.argv[1]+'")')
			if error:print(error.as_string())
			if WINDOW:raise Exception('Passing to repl')
	except:
		try:
			while _E:
				text=input('phlang > ')
				if text.strip()=='':continue
				result,error=run('<stdin>',text)
				if error:print(error.as_string())
				elif result:
					if len(result.elements)==1:print(repr(result.elements[0]))
					else:print(repr(result))
		except Exception as e:print('Uncaught exception:',e);main()
if __name__=='__main__':main()