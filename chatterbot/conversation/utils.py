import time
from tqdm import tqdm

def get_response_statements(statement_list):
    """
    Filter out all statements that are not in response to another statement.
    A statement must exist which lists the closest matching statement in the
    in_response_to field. Otherwise, the logic adapter may find a closest
    matching statement that does not have a known response.
    """
    responses = set()
    to_remove = list()
    

    # for statement in statement_list:
    #     for response in statement.in_response_to:
    #         responses.add(response.text)

    # for statement in statement_list:
    #     if statement.text not in responses:
    #         to_remove.append(statement)

    # # KORY: Remove the response statement issue to speed things up.
    # # This is an exponential time suck, is this a necessary code bit

    # for statement in tqdm(to_remove):
    #     statement_list.remove(statement)
    
    return statement_list
