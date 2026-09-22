import json

from main import main


class TestMain:
    def test_default_run_prints_ascii_grid_and_summary(self, capsys):
        main(["--seed", "1"])
        out = capsys.readouterr().out

        assert "#" in out  # wall tiles from the rendered grid
        assert "rooms" in out
        assert "corridors" in out

    def test_json_output_is_valid_json(self, capsys):
        main(["--seed", "1", "--json"])
        out = capsys.readouterr().out

        data = json.loads(out)
        assert data["seed"] == 1
        assert "rooms" in data
        assert "corridors" in data
        assert "grid" not in data  # --grid not passed

    def test_json_output_includes_grid_when_requested(self, capsys):
        main(["--seed", "1", "--json", "--grid"])
        out = capsys.readouterr().out

        data = json.loads(out)
        assert "grid" in data

    def test_image_output_writes_file(self, tmp_path, capsys):
        out_path = tmp_path / "dungeon.png"
        main(["--seed", "1", "--image", str(out_path)])
        out = capsys.readouterr().out

        assert out_path.exists()
        assert "Saved image" in out

    def test_unseeded_run_does_not_crash(self, capsys):
        main([])
        out = capsys.readouterr().out

        assert "rooms" in out
