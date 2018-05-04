from .views import app
from .models import graph


def create_unique_constraint(label, property):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    query = query.format(label=label, property=property)
    graph.run(query)

create_unique_constraint("User", "username")
create_unique_constraint("Question", "id")
create_unique_constraint("Topic", "topic")
create_unique_constraint("Reply", "id")
