""" 
Utility functions for processing data from adamkarvonen/chess_games before training. 
"""


def combine_columns_map(example):
    """ """
    transcript = "1." + example["transcript"].split("1.", 1)[-1]
    return {"transcript": transcript}


class TokenizeMap:
    """
    A `Map` which tokenizes the transcript column of a batch of examples.
    """

    def __init__(self, tokenizer, context_length):
        self.tokenizer = tokenizer
        self.context_length = context_length

    def tokenize(self, element):
        outputs = self.tokenizer(
            element["transcript"],
            return_tensors="np",
            truncation=True,
            max_length=self.context_length,
            return_overflowing_tokens=True,
            return_length=True,
        )
        input_batch = []
        for length, input_ids in zip(outputs["length"], outputs["input_ids"]):
            if length == self.context_length:
                input_batch.append(input_ids)
        return {"input_ids": input_batch}
