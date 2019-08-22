import math
from hypothesis import given, settings
import hypothesis.strategies as st
from rdflib import Graph, Literal, BNode, Namespace, URIRef
from rdflib.namespace import FOAF, XSD
import statemachine
import unittest

g = Graph()

g.bind("foaf", FOAF)


@given(st.integers())
def test_insert_to_graph(teststring):
    if not teststring:
        return None
    donna = BNode()
    g.add((donna, FOAF.age, Literal(teststring)))
    assert g.value(donna, FOAF.age) == Literal(teststring)
    g.remove((donna, FOAF.age, None))


def make_graph():
    xx = Graph()
    xx.bind("foaf", FOAF)
    return xx


@settings(deadline=900)
@given(st.text())
def test_add_and_query(s):
    if not s:
        return None
    _donna = BNode()
    graph = make_graph()
    graph.add((_donna, FOAF.name, Literal(s)))
    qres = graph.query(
        """SELECT DISTINCT ?aname
           WHERE {
              ?a foaf:name ?aname .
           }""")
    if len(qres) > 1:
        return ""
    res = ""
    for r in qres:
        res = str(r[0])
    assert res == s


_invalid_uri_chars = '<>" {}|\\^`'


@given(st.text(st.characters(max_codepoint=1000, blacklist_characters=_invalid_uri_chars), min_size=1), st.floats())
def test_float_as_input(s, f):
    a = Graph()
    node = URIRef('http://www.w3.org/2002/07/owl#/%s/'%s)
    a.add((node, XSD.float, Literal(f)))
    if math.isnan(float(a.value(node, XSD.float))) and math.isnan(float(f)):
        return None
    assert float(a.value(node, XSD.float)) == float(f)


@given(st.text(st.characters(max_codepoint=1000, blacklist_characters=_invalid_uri_chars), min_size=1), st.floats())
def test_parsing_of_float(s, f):
    a = Graph()
    b = Graph()
    node = URIRef('http://www.w3.org/2002/07/owl#/%s/'%s)
    a.add((node, XSD.float, Literal(f)))
    b.parse(data=a.serialize(format="turtle").decode("utf-8"), format='turtle')
    if math.isnan(float(a.value(node, XSD.float))) and math.isnan(float(f)):
        return None
    print(float(a.value(node, XSD.float)) ,float(b.value(node, XSD.float)))
    assert float(a.value(node, XSD.float)) == float(b.value(node, XSD.float))


@given(st.text(st.characters(max_codepoint=1000, blacklist_characters=_invalid_uri_chars), min_size=1))
def test_namespace(s):
    owl = Namespace('http://www.w3.org/2002/07/owl#')
    assert owl[s] == URIRef(u'http://www.w3.org/2002/07/owl#%s')%s


def _is_valid_uri(uri):
    for c in _invalid_uri_chars:
        if c in uri: return False
    return True


@given(st.characters(blacklist_characters=_invalid_uri_chars))
def test_valid_uri(s):
    test_string = '%s'%s
    if test_string:
        assert _is_valid_uri(test_string) == True


twoints = st.tuples(st.characters(), st.characters())


@given(st.lists(twoints, unique_by=(lambda x: x[0], lambda x: x[1])))
def test_valid_uri2(s):
    assert _is_valid_uri(s) == True


number_of_lists = st.integers(min_value=1, max_value=50)
list_lengths = st.integers(min_value=0, max_value=5)


def build_strategy(number_and_length):
    number, length = number_and_length
    list_elements = st.characters()
    return st.lists(
        st.lists(list_elements, min_size=length, max_size=length),
        min_size=number, max_size=number)


mystrategy = st.tuples(number_of_lists, list_lengths).flatmap(build_strategy)


@given(mystrategy)
def test_namespace2(s):
    owl = Namespace('http://www.w3.org/2002/07/owl#')
    uri = URIRef(u'http://www.w3.org/2002/07/owl#%s') % s
    assert owl[str(s)] == uri


TestDBComparison = statemachine.DatabaseComparison.TestCase
print("Test running")
if __name__ == '__main__':
    test_insert_to_graph()
    test_add_and_query()
    test_namespace()
    test_valid_uri()
    test_valid_uri2()
    test_namespace2()
    test_float_as_input()
    test_parsing_of_float()
    unittest.main()
