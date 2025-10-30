# main.py
from __future__ import annotations
from datetime import datetime, UTC
from typing import List

from sqlalchemy import (
    create_engine, Integer, String, DateTime, Boolean, Float,
    ForeignKey, Table, Column ,select, update, delete
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,Session
)

import random

engine = create_engine("sqlite:///experiments.db", echo=True)


class Base(DeclarativeBase):
    pass


# --- Tabela skojarzeń many-to-many (Subject <-> Experiment)

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("subject_id", ForeignKey("subject.id"), primary_key=True),
    Column("experiment_id", ForeignKey("experiment.id"), primary_key=True),
)


class Experiment(Base):
    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # M:N 
    subjects: Mapped[List["Subject"]] = relationship(
        "Subject",
        secondary="enrollments",
        back_populates="experiment",
    )

    # 1:N — jeden Experiment ma wiele DataPointów
    data_points: Mapped[List["DataPoint"]] = relationship(
        "DataPoint",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )


class DataPoint(Base):
    __tablename__ = "data_point"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    real_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)

    # klucz obcy do Experiment (strona "N")
    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("experiment.id"), nullable=False
    )
    experiment: Mapped["Experiment"] = relationship(
        "Experiment", back_populates="data_points"
    )


class Subject(Base):
    __tablename__ = "subject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gdpr_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # symetryczna strona M:N
    experiments: Mapped[List[Experiment]] = relationship(
        "Experiment",
        secondary="enrollments",
        back_populates="subject",
    )


if __name__ == "__main__":
    # Base.metadata.create_all(engine)

    #     # 1. Dodaj 2 wiersze do Experiments
    # with Session(engine) as session:
    #     exp1 = Experiment(title="Exp A", type=1)
    #     exp2 = Experiment(title="Exp B", type=2)
    #     session.add_all([exp1, exp2])
    #     session.flush()  

    #     # 2. Dodaj 10 wierszy do DataPoints (losowe wartości) przypisując do eksperymentów
    #     points_exp1 = [
    #         DataPoint(real_value=random.uniform(0.0, 1.0),
    #                   target_value=random.uniform(0.0, 1.0),
    #                   experiment=exp1)
    #         for _ in range(5)
    #     ]
    #     points_exp2 = [
    #         DataPoint(real_value=random.uniform(0.0, 1.0),
    #                   target_value=random.uniform(0.0, 1.0),
    #                   experiment=exp2)
    #         for _ in range(5)
    #     ]
    #     session.add_all(points_exp1 + points_exp2)

    #     # Zmiany trafiają do bazy dopiero po commit
    #     session.commit()

    # # 3. Pobierz i wyświetl dodane dane (select + scalars)
    # with Session(engine) as session:
    #     experiments = session.scalars(
    #         select(Experiment).order_by(Experiment.id)
    #     ).all()
    #     datapoints = session.scalars(
    #         select(DataPoint).order_by(DataPoint.id)
    #     ).all()

    #     print(f"\nExperiments ({len(experiments)}):")
    #     for e in experiments:
    #         print(
    #             f"  id={e.id}, title={e.title}, created_at(UTC)={e.created_at.isoformat()}, "
    #             f"type={e.type}, finished={e.finished}"
    #         )

    #     print(f"\nDataPoints ({len(datapoints)}):")
    #     for d in datapoints:
    #         print(
    #             f"  id={d.id}, real_value={d.real_value:.4f}, "
    #             f"target_value={d.target_value:.4f}, experiment_id={d.experiment_id}"
    #         )

    # # 4. Zaktualizuj wszystkie wiersze Experiments na finished=True
    # with Session(engine) as session:
    #     session.execute(update(Experiment).values(finished=True))
    #     session.commit()  # commit kończy transakcję

    # # 5. Usuń wszystkie wiersze z obu tabel
    # with Session(engine) as session:
    #     session.execute(delete(DataPoint))
    #     session.execute(delete(Experiment))
    #     session.commit()
    pass
