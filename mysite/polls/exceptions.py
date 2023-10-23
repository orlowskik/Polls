

class ValidationError(Exception):
    """Exception raised for errors in the input votes.

        Attributes:
            votes   -- number of votes
            message -- explanation of the error
        """

    def __init__(self, votes, message="Number of votes cannot be negative"):
        self.votes = votes
        self.message = message
        super().__init__(self.message)
