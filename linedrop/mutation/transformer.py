from ast import NodeTransformer, Pass, stmt


class Transformer(NodeTransformer):

    def __init__(self, remove_at=None):
        self.items = []
        self.remove_at = remove_at

    def get_statement(self, node):
        if isinstance(node, stmt):
            return (node.lineno, str(node))

    def visit(self, node):
        statement = self.get_statement(node)
        if statement:
            if len(self.items) == self.remove_at:
                self.items.append(statement)
                return Pass()
            self.items.append(statement)
        return super(NodeTransformer, self).visit(node)
