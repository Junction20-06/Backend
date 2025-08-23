# Backend/app/models/node.py

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from app.core.database import Base
from app.schemas.node import NodeStatus

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)    # 수학Ⅰ, 수학Ⅱ, ...
    concept = Column(String, nullable=False)    # 핵심 개념
    element = Column(String, nullable=False)    # 내용 요소
    status = Column(
        Enum(NodeStatus),  # 가져온 NodeStatus Enum을 사용합니다.
        default=NodeStatus.not_started,
        server_default=NodeStatus.not_started.value, # .value를 추가하여 문자열 값으로 설정
        nullable=False
    )

class ProfileNodeDetail(Base):
    __tablename__ = "profile_node_details"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    score = Column(Integer, default=0, nullable=False)