class DatabaseService:
    def __init__(self) -> None:
        raise NotImplementedError
    
    def get_question_by_id(self, question_id: int) -> dict:
        raise NotImplementedError

    def get_answer_by_question_id(self, question_id: int) -> dict:
        raise NotImplementedError