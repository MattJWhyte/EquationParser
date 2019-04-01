import math


class Term:

    OP_SIN = 0
    OP_COS = 1
    OP_TAN = 2
    OP_ABS = 3

    def __init__(self, exp, positive, sub_equations):
        self.exp = exp
        self.positive = positive
        self.sub_equations = sub_equations

    def get_value(self, **var):
        try:
            exp = self.exp
            components = []
            last_index = -1
            for i in xrange(len(exp)):
                if exp[i] == "*" or exp[i] == "/":
                    components.append(exp[last_index + 1:i])
                    last_index = i
                    components.append(exp[i])
            components.append(exp[last_index + 1:])

            val = self.__evaluate_component(components[0], **var)
            for i in xrange(1, len(components) - 1, 2):
                if components[i] == "*":
                    val = val * self.__evaluate_component(components[i + 1], **var)
                elif components[i] == "/":
                    div = self.__evaluate_component(components[i + 1], **var)
                    val = val / div

            return val * (1 if self.positive else -1)

        except ZeroDivisionError or ValueUndefinedError:
            raise ValueUndefinedError

    def __evaluate_component(self, comp, **var):
        if comp.__contains__("^"):
            parts = comp.split("^")
            base = self.__evaluate_component(parts[0], **var)
            power = self.__evaluate_component(parts[1], **var)
            return base**power
        elif comp[0] == "@":
            operand = self.__evaluate_component(comp[2:], **var)
            code = int(comp[1])
            if code == Term.OP_SIN:
                return math.sin(operand*math.pi/180.0)
            if code == Term.OP_COS:
                return math.cos(operand*math.pi/180.0)
            if code == Term.OP_TAN:
                return math.tan(operand*math.pi/180.0)
            if code == Term.OP_ABS:
                return abs(operand)
        elif comp[0] == "{":
            return self.__evaluate_sub_eqn(comp, **var)
        elif comp.isalpha():
            if comp in var:
                return float(var[comp])
            else:
                raise UndefinedVariableError(comp)
        else:
            try:
                return float(comp)
            except ValueError:
                raise InvalidComponentError

    def __evaluate_sub_eqn(self, exp, **var):
        index = int(exp[1:])
        sub_eqn = self.sub_equations[index]
        return sub_eqn.get_value(**var)

    def __str__(self):
        return "%s - %i" % (self.exp, self.positive)


class Equation:

    def __init__(self, exp):

        self.exp = exp
        self.sub_equations = []
        self.formatted_exp = exp
        self.variables = []

        bracket_indices = []
        replacements = []

        for i in range(len(exp)):
            if exp[i] == "(":
                bracket_indices.append(i)
            elif exp[i] == ")":
                start_index = bracket_indices[-1]
                bracket_indices.pop()
                if len(bracket_indices) == 0:
                    # Get replacement count
                    replacement_count = len(self.sub_equations)
                    replacements.append([replacement_count, exp[start_index:i+1]])
                    self.sub_equations.append(Equation(exp[start_index+1:i]))

        self.formatted_exp = self.formatted_exp.replace("sin", "@%i" % Term.OP_SIN)
        self.formatted_exp = self.formatted_exp.replace("cos", "@%i" % Term.OP_COS)
        self.formatted_exp = self.formatted_exp.replace("tan", "@%i" % Term.OP_TAN)
        self.formatted_exp = self.formatted_exp.replace("abs", "@%i" % Term.OP_ABS)

        for i in xrange(len(self.formatted_exp)):
            if (self.formatted_exp[i] + "").isalpha():
                self.variables.append(exp[i])

        for t in replacements:
            self.formatted_exp = self.formatted_exp.replace(t[1], "{%i" % t[0])

        terms = self.formatted_exp.split(" ")

        self.terms = []

        # Check first term
        if terms[0][0] == "-":
            self.terms.append(Term(terms[0][1:], False, self.sub_equations))
        else:
            self.terms.append(Term(terms[0], True, self.sub_equations))

        for i in xrange(1, len(terms)-1, 2):
            positive = terms[i] == "+"
            self.terms.append(Term(terms[i+1], positive, self.sub_equations))

    def get_value(self, **var):
        try:
            val = 0
            for i in xrange(len(self.terms)):
                val += self.terms[i].get_value(**var)
            return val
        except ZeroDivisionError or ValueUndefinedError:
            raise ValueUndefinedError


class InvalidComponentError(Exception):

    def __init__(self, component):
        self.message = "%s cannot be evaluated" % component

    def __str__(self):
        return str(self.message)


class UndefinedVariableError(Exception):

    def __init__(self, var):
        self.message = "'%s' has not been given a value in method call" % var

    def __str__(self):
        return str(self.message)


class ValueUndefinedError(Exception):

    def __str__(self):
        return "Division by Zero (0) took place"
