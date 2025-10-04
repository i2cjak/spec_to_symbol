from prompt_toolkit.completion import Completer, Completion
from spec_to_symbol.fuzzy import footprint_finder

class FootprintCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if len(text) < 2:
            return
            
        results = footprint_finder.find(text)
        for result in results:
            yield Completion(result, start_position=-len(text))
