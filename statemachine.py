from collections import defaultdict
import hypothesis.strategies as st
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule


class DatabaseComparison(RuleBasedStateMachine):
    def __init__(self):
        super(DatabaseComparison, self).__init__()
        self.database = Graph()
        self.database.bind("foaf", FOAF)
        self.model = defaultdict()

    keys = Bundle('keys')
    values = Bundle('values')
    _invalid_uri_chars = '<>" {}|\\^`'

    @rule(target=keys, k=st.text(st.characters(max_codepoint=1000, blacklist_characters=_invalid_uri_chars), min_size=1))
    def add_key(self, k):
        return k

    @rule(target=values, v=st.integers())
    def add_value(self, v):
        return v

    @rule(k=keys, v=values)
    def save(self, k, v):
        self.model[k] = v
        node = URIRef("http://example.org/people/%s" % k)
        self.database.set((node, FOAF.value, Literal(v)))

    @rule(k=keys)
    def delete(self, k):
        self.model[k] = None
        node = URIRef("http://example.org/people/%s" % k)
        self.database.remove((node, FOAF.value, None))

    @rule(k=keys)
    def values_agree(self, k):
        node = URIRef("http://example.org/people/%s" % k)
        assert str(self.database.value(node, FOAF.value)) == str(self.model.get(k))


