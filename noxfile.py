from nox_poetry import Session, session


@session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session: Session):
    session.install(".")
    session.install("pytest")
    session.run("pytest")
