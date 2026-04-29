from netbubbles.layout import (
    bilayer,
    circular,
    focus,
    grid,
    manual,
)


class TestCircular:
    def test_count(self):
        assert len(circular(["A", "B", "C"])) == 3

    def test_2d_coords(self):
        for p in circular(["A", "B", "C"]).values():
            assert len(p) == 2

    def test_order(self):
        pos = circular(["C", "A", "B"], order=["A", "B", "C"])
        assert list(pos.keys()) == ["A", "B", "C"]

    def test_single_node(self):
        assert len(circular(["A"])) == 1

    def test_radius(self):
        x, y = circular(["A"], radius=5.0)["A"]
        assert abs((x ** 2 + y ** 2) ** 0.5 - 5.0) < 1e-9


class TestFocus:
    def test_center_at_origin(self):
        assert focus(["A", "B", "C"], center="A")["A"] == (0.0, 0.0)

    def test_count(self):
        assert len(focus(["A", "B", "C"], center="A")) == 3

    def test_only_center(self):
        pos = focus(["A"], center="A")
        assert pos["A"] == (0.0, 0.0)
        assert len(pos) == 1


class TestBilayer:
    def test_count(self):
        assert len(bilayer(["A", "B"], ["C", "D"])) == 4

    def test_inner_closer_than_outer(self):
        pos = bilayer(["A"], ["B"], inner_radius=0.5, outer_radius=2.0)
        ri = (pos["A"][0] ** 2 + pos["A"][1] ** 2) ** 0.5
        ro = (pos["B"][0] ** 2 + pos["B"][1] ** 2) ** 0.5
        assert ri < ro

    def test_empty_outer(self):
        pos = bilayer(["A"], [])
        assert len(pos) == 1


class TestGrid:
    def test_count(self):
        assert len(grid(["A", "B", "C", "D"])) == 4

    def test_single(self):
        assert grid(["A"])["A"] == (0.0, 0.0)

    def test_spacing(self):
        pos = grid(["A", "B"], spacing=3.0)
        assert pos["B"][0] == 3.0


class TestManual:
    def test_passthrough(self):
        assert manual({"A": (1.0, 2.0)})["A"] == (1.0, 2.0)

    def test_returns_copy(self):
        src = {"A": (0.0, 0.0)}
        assert manual(src) is not src
