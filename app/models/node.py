# Backend/app/models/node.py

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from app.core.database import Base
from app.schemas.node import NodeStatus

class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    element = Column(String, nullable=False)

class ProfileNodeDetail(Base):
    __tablename__ = "profile_node_details"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(
        Enum(NodeStatus),
        default=NodeStatus.not_started,
        nullable=False
    )