class DatabaseService:
    def __init__(self) -> None:
        pass
    
    def get_question_by_id(self, question_id: int) -> dict:
        raise NotImplementedError

    def get_answer_by_question_id(self, question_id: int) -> dict:
        # not implemented
        return {"text": "This is a placeholder answer."}