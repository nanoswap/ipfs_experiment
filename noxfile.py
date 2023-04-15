import nox


@nox.session(python=["python3"])
def build(session: nox.Session) -> None:
    session.install("build")
    session.env["PYTHONPATH"] = "src"
    session.run("python", "-m", "build")


@nox.session(python=["python3"])
def tests(session: nox.Session) -> None:
    session.install("-r", "requirements.txt")
    session.install("-r", "requirements-dev.txt")
    session.install('pytest')
    session.install("pytest-cov")
    session.env["PYTHONPATH"] = "src"
    session.run("pytest", "--cov=src")


@nox.session
def lint(session):
    session.install('flake8')
    session.run('flake8')
