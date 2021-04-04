import math


class State():
    def __init__(self, CL, ML, boat, CR, MR, ):

        self.CL = CL
        self.ML = ML
        self.boat = boat
        self.CR = CR
        self.MR = MR
        self.parent_node = None

    def Check_Validity(self):
        if self.ML >= 0 and self.MR >= 0 and self.CL >= 0 and self.CR >= 0 and (
                self.ML == 0 or self.ML >= self.CL) and (self.MR == 0 or self.MR >= self.CR):

            return True
        else:
            return False

    def end_mark(self):
        if self.CL == 0 and self.ML == 0:
            return True
        else:
            return False



def get_next_state(state_now):
    child_nodes = [];
    if state_now.boat == 'left':

        new_state = State(state_now.CL, state_now.ML - 1, 'right',
                          state_now.CR, state_now.MR + 1)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)

        new_state = State(state_now.CL - 1, state_now.ML, 'right',
                          state_now.CR + 1, state_now.MR)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL, state_now.ML - 2, 'right',
                          state_now.CR, state_now.MR + 2)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL - 2, state_now.ML, 'right',
                          state_now.CR + 2, state_now.MR)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL - 1, state_now.ML - 1, 'right',
                          state_now.CR + 1, state_now.MR + 1)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
    else:
        new_state = State(state_now.CL, state_now.ML + 1, 'left',
                          state_now.CR, state_now.MR - 1)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL + 1, state_now.ML, 'left',
                          state_now.CR - 1, state_now.MR)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL, state_now.ML + 2, 'left',
                          state_now.CR, state_now.MR - 2)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL + 2, state_now.ML, 'left',
                          state_now.CR - 2, state_now.MR)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
        new_state = State(state_now.CL + 1, state_now.ML + 1, 'left',
                          state_now.CR - 1, state_now.MR - 1)

        if new_state.Check_Validity():
            new_state.parent_node = state_now
            child_nodes.append(new_state)
    return child_nodes


def BFS():
    initial_state = State(3, 3, 'left', 0, 0)
    visited = list()
    explored = set()
    visited.append(initial_state)
    while visited:
        condition = visited.pop(0)
        if condition.end_mark():
            return condition
        explored.add(condition)
        child_nodes = get_next_state(condition)
        for child_nodes in child_nodes:
            if (child_nodes not in explored) or (child_nodes not in visited):
                visited.append(child_nodes)
    return None


def main():
    result = BFS()

    print("(CL,ML,boat,CR,MR)")

    path = []
    path.append(result)
    parent_node = result.parent_node
    while parent_node:
        path.append(parent_node)
        parent_node = parent_node.parent_node

    for t in range(len(path)):
        state = path[len(path) - t - 1]
        print("(" + str(state.CL) + "," + str(state.ML) + "," + state.boat + "," + str(state.CR) + "," + str(state.MR) + ")\n")

    print("Succeded")


if __name__ == "__main__":
    main()


