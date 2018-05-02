from .views import app
from .models import graph

'''
def create_unique_constraint(label, property):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    query = query.format(label=label, property=property)
    graph.cypher.execute(query)

create_unique_constraint("user", "username")
create_unique_constraint("question", "id")
create_unique_constraint("topic", "id")
create_unique_constraint("reply", "name")
'''
