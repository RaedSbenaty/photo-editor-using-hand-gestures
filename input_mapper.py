from choice import Choice
from posture import Posture


class Input_Mapper:
    modes = [Choice.SELECT, Choice.PAINT]
    without_mode_input_mapper = {
        Posture.TWO_LEFT: Choice.SCALE,
        Posture.TWO_RIGHT: Choice.ROTATE,
        Posture.TWO_MIDDLE: Choice.TRANSLATE,
        Posture.FIVE_LEFT: Choice.SELECT,
        Posture.FIVE_RIGHT: Choice.SAVE,
        Posture.ONE_NORMAL: Choice.PAINT,
        Posture.FOUR: Choice.CLEAR,
        Posture.ZERO: Choice.NOTHING
    }

    def __init__(self) -> None:
        self.mode = None

    def map(self, posture: Posture) -> Choice:
        choice = None # output 
        if self.mode in self.modes:
            choice = self.mode_map(posture)
        if choice is None :# ==> either mode is none or the posture is not in the set of the mode (e.g chose save from paint mode )
            choice = self.without_mode_input_mapper[posture]
        if choice in self.modes:
            self.mode = choice
        elif choice == Choice.NOTHING:
            self.mode = None
        return choice

    def mode_map(self, posture: Posture) -> Choice:
        if posture == Posture.TWO_MIDDLE:
            return Choice.CLICK
        elif posture == Posture.TWO_LEFT:
            return Choice.SIZE_INC
        elif posture == Posture.TWO_RIGHT:
            return Choice.SIZE_DEC

mapper = Input_Mapper()
#test case 1: scale,select,click,save
def test_case_1(mapper):
    print(mapper.map(Posture.TWO_LEFT))
    print(mapper.map(Posture.FIVE_LEFT))
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.FIVE_RIGHT))


#test case 2: select,paint,size_inc,click,nothing
def test_case_2(mapper):
    print(mapper.map(Posture.FIVE_LEFT))
    print(mapper.map(Posture.ONE_NORMAL))
    print(mapper.map(Posture.TWO_LEFT))
    print(mapper.map(Posture.TWO_MIDDLE))
    print(mapper.map(Posture.ZERO))

test_case_2(mapper)
