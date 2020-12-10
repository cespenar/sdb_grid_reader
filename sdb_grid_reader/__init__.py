import glob
import itertools
import os
import re

import mesa_reader as mesa
import numpy as np
import pandas as pd
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Model(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    m_i = Column(Float, nullable=False)
    m_env = Column(Float, nullable=False)
    rot_i = Column(Float, nullable=False)
    z_i = Column(Float, nullable=False)
    y_i = Column(Float, nullable=False)
    fh = Column(Float, nullable=False)
    fhe = Column(Float, nullable=False)
    fsh = Column(Float, nullable=False)
    mlt = Column(Float, nullable=False)
    sc = Column(Float, nullable=False)
    reimers = Column(Float, nullable=False)
    blocker = Column(Float, nullable=False)
    turbulence = Column(Float, nullable=False)
    m = Column(Float, nullable=False)
    rot = Column(Float, nullable=False)
    model_number = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    m_he_core = Column(Float, nullable=False)
    log_Teff = Column(Float, nullable=False)
    log_g = Column(Float, nullable=False)
    log_L = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)
    age = Column(Float, nullable=False)
    z_surf = Column(Float, nullable=False)
    y_surf = Column(Float, nullable=False)
    center_he4 = Column(Float, nullable=False)
    custom_profile = Column(Float, nullable=False)
    top_dir = Column(String, nullable=False)
    log_dir = Column(String, nullable=False)


class SdbGridReader():
    """

    """

    