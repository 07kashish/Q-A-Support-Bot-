

class ConversationMemory:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history = []

    def add(self, question: str, answer: str):
        self.history.append({
            "question": question,
            "answer": answer
        })
       
        self.history = self.history[-self.max_turns :]

    def get_context(self) -> str:
        if not self.history:
            return ""
        context = []
        for turn in self.history:
            context.append(f"User: {turn['question']}")
            context.append(f"Assistant: {turn['answer']}")
        return "\n".join(context)
