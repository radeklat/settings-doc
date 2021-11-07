from _pytest.fixtures import fixture
from typer.testing import CliRunner


@fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()
