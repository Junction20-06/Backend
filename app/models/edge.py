from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id"))
    to_node_id = Column(Integer, ForeignKey("nodes.id"))

