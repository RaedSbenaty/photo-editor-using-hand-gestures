from choice import Choice
from posture import Posture


class Input_Mapper:

    def __init__(self) -> None:
        self.state_graph = {
            Choice.NOTHING: {
                Posture.ZERO: Choice.NOTHING,

                Posture.ONE_NORMAL: Choice.PAINT,

                Posture.TWO_LEFT: Choice.SCALE,
                Posture.TWO_RIGHT: Choice.ROTATE,
                Posture.TWO_MIDDLE: Choice.TRANSLATE,

                Posture.THREE_LEFT: Choice.NOTHING,  # unused
                Posture.THREE_RIGHT: Choice.NOTHING,  # unused
                Posture.THREE_MIDDLE: Choice.NOTHING,  # unused

                Posture.FOUR_RIGHT: Choice.NOTHING,  # unsused
                Posture.FOUR_LEFT: Choice.NOTHING,  # unsused

                Posture.FIVE_LEFT: Choice.SELECT,
                Posture.FIVE_RIGHT: Choice.SAVE,

                Posture.FIVE_RIGHT_SIDE: Choice.NOTHING,  # unused
                Posture.FIVE_LEFT_SIDE: Choice.NOTHING,  # unused
                Posture.NONE: Choice.NOTHING,  # unused

            },
            Choice.SELECT: {
                Posture.TWO_LEFT: Choice.SIZE_INC,
                Posture.TWO_RIGHT: Choice.SIZE_DEC,
                Posture.TWO_MIDDLE: Choice.CLICK
            },
            Choice.PAINT: {
                Posture.TWO_LEFT: Choice.SIZE_INC,
                Posture.TWO_RIGHT: Choice.SIZE_DEC,
                Posture.TWO_MIDDLE: Choice.CLICK,
                Posture.FOUR_LEFT: Choice.CLEAR
            },
            Choice.CLEAR: {
                Posture.TWO_LEFT: Choice.SIZE_INC,
                Posture.TWO_RIGHT: Choice.SIZE_DEC,
                Posture.TWO_MIDDLE: Choice.CLICK,
                Posture.ONE_NORMAL: Choice.PAINT
            }
        }
        self.current_choice = Choice.NOTHING

    def map(self, posture: Posture) -> Choice:
        print(type(posture))
        assert(type(posture) is Posture)
        out = self.get_choice_or_default(posture)
        if out in self.state_graph: # change the state only if the new choice has nested postures 
            self.current_choice = out
        return out 

    def get_menu_of(self,choice:Choice) :
        return self.state_graph.get(choice,self.state_graph[Choice.NOTHING])

    def get_choice_or_default(self,posture) -> Choice :
        current_menu = self.get_menu_of(self.current_choice)
        print(f"{posture in self.state_graph[Choice.NOTHING]=},{self.state_graph[Choice.NOTHING]=}")
        root_choice =self.state_graph[Choice.NOTHING][posture]
        print(f"{posture in current_menu}")
        return current_menu.get(posture, root_choice)

mapper = Input_Mapper()



# test case 1: scale,select,click,save
def test_case_1(mapper):
    print(mapper.map(Posture.TWO_LEFT))
    print(mapper.map(Posture.FIVE_LEFT))
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.FIVE_RIGHT))


# test case 2: select,paint,size_inc,click,nothing
def test_case_2(mapper):
    print(mapper.map(Posture.FIVE_LEFT))
    print(mapper.map(Posture.ONE_NORMAL))
    print(mapper.map(Posture.TWO_LEFT))
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.ZERO))

# test case 3: rotate,paint,size_inc,click,nothing
def test_case_3(mapper):
    print(mapper.map(Posture.TWO_RIGHT))
    print(mapper.map(Posture.ONE_NORMAL))
    print(mapper.map(Posture.TWO_LEFT))
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.ZERO))

# test case 4: translate,paint,size_inc,click,nothing
def test_case_4(mapper):
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.ONE_NORMAL))
    print(mapper.map(Posture.TWO_LEFT))
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.ZERO))


test_case_4(mapper)