from choice import Choice
from posture import Posture


class Input_Mapper:

    def __init__(self) -> None:
        self.state_graph = {
            Choice.NOTHING: {
                Posture.TWO_LEFT: Choice.SCALE,
                Posture.TWO_RIGHT: Choice.ROTATE,
                Posture.TWO_MIDDLE: Choice.TRANSLATE,
                Posture.FIVE_LEFT: Choice.SELECT,
                Posture.FIVE_RIGHT: Choice.SAVE,
                Posture.ONE_NORMAL: Choice.PAINT,
                Posture.ZERO:Choice.NOTHING
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
                Posture.FOUR: Choice.CLEAR
            },
            Choice.CLEAR: {
                Posture.TWO_LEFT: Choice.SIZE_INC,
                Posture.TWO_RIGHT: Choice.SIZE_DEC,
                Posture.TWO_MIDDLE: Choice.CLICK,
                Posture.ONE_NORMAL: Choice.PAINT
            }
        }
        self.current_state = Choice.NOTHING

    def map(self, posture: Posture) -> Choice:
        self.current_state = self.state_graph[self.current_state][posture]\
             if self.current_state in self.state_graph and posture in self.state_graph[self.current_state] \
                else self.state_graph[Choice.NOTHING][posture]
        return self.current_state


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


test_case_2(mapper)
