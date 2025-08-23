def update_node_status(correct_rate: float) -> str:
    """정답률 기반 노드 상태 결정"""
    if correct_rate > 0.8:
        return "strong"
    elif correct_rate < 0.5:
        return "weak"
    else:
        return "neutral"

