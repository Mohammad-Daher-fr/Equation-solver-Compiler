from typing import List
import ply.lex as lex
import ply.yacc as yacc
import numpy as np


import numpy.linalg as la

# ==== AST Nodes ====


class Term:
    def __init__(self, coef: float, var: str):
        self.coef = coef
        self.var = var

    def __repr__(self):
        return f"{self.coef}{self.var}"


class Equation:
    def __init__(self, terms: List[Term], value: float):
        self.terms = terms
        self.value = value

    def __repr__(self):
        return " + ".join(map(str, self.terms)) + f" = {self.value}"


class System:
    def __init__(self, equations: List[Equation]):
        self.equations = equations

    def __repr__(self):
        return "\n".join(map(str, self.equations))


# ==== Lexer ====


class Lexer:
    tokens = ("NUMBER", "ID", "PLUS", "MINUS", "EQUALS")

    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_EQUALS = r"="

    def t_NUMBER(self, t):
        r"-?\d+(\.\d+)?"
        t.value = float(t.value)
        return t

    def t_ID(self, t):
        r"[a-zA-Z]"
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise SyntaxError(f"Illegal character '{t.value[0]}'")

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def tokenize(self, data: str):
        self.lexer.input(data)
        return list(iter(self.lexer.token, None))


# ==== Parser ====


class Parser:
    tokens = Lexer.tokens

    def __init__(self):
        # create your lexer instance…
        self._lexer_obj = Lexer()
        # …and pass it explicitly to the parser
        self.parser = yacc.yacc(module=self)

    def parse(self, data: str) -> System:
        # use the lexer you instantiated
        return self.parser.parse(data, lexer=self._lexer_obj.lexer)

    def p_system(self, p):
        """system : equation
        | equation system"""
        if len(p) == 2:
            p[0] = System([p[1]])
        else:
            p[0] = System([p[1]] + p[2].equations)

    def p_equation(self, p):
        """equation : expression EQUALS NUMBER"""
        p[0] = Equation(p[1], p[3])

    def p_expression(self, p):
        """expression : term
        | term PLUS expression
        | term MINUS expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            sign = 1 if p[2] == "+" else -1
            for t in p[3]:
                t.coef *= sign
            p[0] = [p[1]] + p[3]

    def p_term(self, p):
        """term : NUMBER ID
        | ID
        | MINUS ID"""
        # NUMBER ID => e.g. 2x
        if len(p) == 3 and p.slice[1].type == "NUMBER":
            p[0] = Term(p[1], p[2])
        # MINUS ID => e.g. -x
        elif len(p) == 3 and p.slice[1].type == "MINUS":
            p[0] = Term(-1.0, p[2])
        # bare ID => coefficient 1
        else:
            p[0] = Term(1.0, p[1])

    def p_error(self, p):
        raise SyntaxError("Syntax error in input")


# ==== Visitors ====


class Visitor:
    def visit(self, node):
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")


class PrettyPrinter(Visitor):
    def visit_System(self, node):
        return "\n".join(self.visit(eq) for eq in node.equations)

    def visit_Equation(self, node):
        parts = []
        for t in node.terms:
            if t.coef == 1:
                parts.append(f"{t.var}")
            elif t.coef == -1:
                parts.append(f"-{t.var}")
            else:
                parts.append(f"{t.coef}{t.var}")
        return " + ".join(parts).replace("+ -", "- ") + f" = {node.value}"


class SolverVisitor(Visitor):
    def visit_System(self, node):
        variables = sorted(set(t.var for eq in node.equations for t in eq.terms))
        var_index = {v: i for i, v in enumerate(variables)}
        A = np.zeros((len(node.equations), len(variables)))
        B = np.zeros(len(node.equations))

        for i, eq in enumerate(node.equations):
            for term in eq.terms:
                A[i][var_index[term.var]] += term.coef
            B[i] = eq.value

        if A.shape[0] != A.shape[1]:
            raise ValueError(
                "Le systeme doit avoir autant d'equations que d'inconnues pour etre resolu directement."
            )

        try:
            solution = la.solve(A, B)
            return dict(zip(variables, solution))
        except la.LinAlgError:
            print(
                "Systeme singulier. Resolution par pseudo-inverse (solution approchee)."
            )
            solution = la.pinv(A) @ B
            return dict(zip(variables, solution))


# ==== Compiler ====


class Compiler:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.pretty_printer = PrettyPrinter()
        self.solver = SolverVisitor()

    def compile(self, filepath: str):
        try:
            with open(filepath, "r") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                print("Le fichier est vide.")
                return

            # Vérification basique de structure : chaque ligne doit contenir '='
            for i, line in enumerate(lines):
                if "=" not in line:
                    raise SyntaxError(
                        f"Ligne {i+1} invalide : \"{line}\". Il manque le signe '='."
                    )

            data = "\n".join(lines)

            print("Lecture du fichier...")
            tokens = self.lexer.tokenize(data)
            print("Analyse lexicale : OK")

            ast = self.parser.parse(data)
            if not ast or not ast.equations:
                print("Aucune équation détectée.")
                return

            print("Analyse syntaxique : OK")
            print("\nPretty printer formate :")
            print(self.pretty_printer.visit(ast))

            print("\n Solution :")
            solution = self.solver.visit(ast)
            for var, val in solution.items():
                print(f"{var} = {val}")

        except FileNotFoundError:
            print(f"Fichier non trouvé : {filepath}")
        except SyntaxError as e:
            print(f"Erreur de syntaxe : {e}")
            print(
                "Syntaxe attendue : des équations du type `2x + 3y = 5`, `-x + y = 0`, etc."
            )
        except ValueError as ve:
            print(f"{ve}")
        except Exception as e:
            print(f"Erreur inattendue : {e}")


# Exemple d'appel
# compiler = Compiler()
# compiler.compile("equations.txt")
