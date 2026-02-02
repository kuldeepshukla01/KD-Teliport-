from agent.llm import LLM

class Corrector:
    def __init__(self, config):
        self.config = config
        self.llm = LLM(config)

    def correct(self, command, error_output):
        prompt = f"""
The user tried to run this command:
{command}

It failed with this error:
{error_output}

Please suggest a corrected command. Output ONLY the corrected command, no explanation.
"""
        return self.llm.generate({}, prompt)
