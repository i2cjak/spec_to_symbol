import re

class SexpAtom(str):
    """A class to represent an unquoted atom in an s-expression, to distinguish it from a string literal."""
    pass

def parse_sexp(sexp_string):
    """
    Parses a string representation of an s-expression into a nested list structure.
    It correctly handles quoted strings vs. unquoted atoms.
    """
    sexp_string = re.sub(r";.*", "", sexp_string) # Remove comments
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', sexp_string)
    return _parse_tokens(tokens)

def _parse_tokens(tokens):
    if not tokens:
        raise ValueError("Unexpected EOF while parsing s-expression.")
    token = tokens.pop(0)
    if token == "(":
        ast = []
        while tokens and tokens[0] != ")":
            ast.append(_parse_tokens(tokens))
        if not tokens:
            raise ValueError("Unexpected EOF: missing ')'")
        tokens.pop(0)
        return ast
    elif token == ")":
        raise ValueError("Unexpected ')'")
    else:
        return _atom(token)

def _atom(token):
    """Converts a token to an int, float, string literal, or SexpAtom."""
    if len(token) > 1 and token.startswith('"') and token.endswith('"'):
        return token[1:-1].replace('\"', '"')
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return SexpAtom(token)

def build_sexp(ast, indent=0):
    """
    Builds a nicely formatted, indented string from a nested list structure,
    correctly handling atoms vs. string literals.
    """
    indent_str = "  " * indent
    if not isinstance(ast, list):
        if isinstance(ast, SexpAtom): return str(ast)
        if isinstance(ast, str): return f'"{ast}"'
        return str(ast)

    if not ast: return "()"

    # Check if the expression should be a single line
    is_simple = all(not isinstance(item, list) for item in ast)
    line_for_check = "(" + " ".join(map(str, ast)) + ")"
    if is_simple and len(line_for_check) < 80:
        return indent_str + "(" + " ".join(build_sexp(item) for item in ast) + ")"

    # Multi-line expression
    first_line = indent_str + "(" + build_sexp(ast[0])
    remaining_items = ast[1:]
    
    # If the second item is not a list, put it on the first line too.
    if len(ast) > 1 and not isinstance(ast[1], list):
        first_line += " " + build_sexp(ast[1])
        remaining_items = ast[2:]

    result = [first_line]
    for item in remaining_items:
        result.append(build_sexp(item, indent + 1))
    
    result.append(indent_str + ")")
    return "\n".join(result)