from nox_poetry import Session, session


@session(python=["3.9", "3.10", "3.11", "3.12"])
def tests(session: Session):
    session.install(".")
    session.install("pytest")
    session.run("pytest")
