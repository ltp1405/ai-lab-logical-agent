from lib.knowledge_base.cell import CellValue
from lib.knowledge_base.world_view import WorldData, WorldView
from rich import print

def test_world_data():
    data = WorldData()
    print(data)
    data[(0, 0)].is_breeze = CellValue.TRUE
    print(data[(0, 0)])

def test_breeze():
    data = WorldView()
    data.set_item((0, 0, "is_breeze"), CellValue.TRUE)
    assert data[(0, 0)].is_breeze == CellValue.TRUE
    print(data[(-1, 0)])
    assert data[(-1, 0)].is_pit == CellValue.MAYBE
    assert data[(0, -1)].is_pit == CellValue.MAYBE
    assert data[(1, 0)].is_pit == CellValue.MAYBE
    assert data[(0, 1)].is_pit == CellValue.MAYBE
    data.set_item((0, -1, "is_pit"), CellValue.FALSE)
    data.set_item((0, 1, "is_pit"), CellValue.FALSE)
    data.set_item((1, 0, "is_pit"), CellValue.FALSE)
    assert data[(1, 0)].is_pit == CellValue.FALSE
    assert data[(0, 1)].is_pit == CellValue.FALSE
    assert data[(0, -1)].is_pit == CellValue.FALSE
    data.set_item((0, 0, "is_breeze"), CellValue.TRUE)
    assert data[(-1, 0)].is_pit == CellValue.TRUE


if __name__ == '__main__':
    test_breeze()