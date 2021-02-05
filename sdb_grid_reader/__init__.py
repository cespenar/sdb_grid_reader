import os
import shutil
from zipfile import ZipFile

import matplotlib.pyplot as plt
import mesa_reader as mesa
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import gyre_data


class SdbGridReader():
    """

    """

    def __init__(self, db_file, grid_dir, zipped_dir=True):
        self.db_file = db_file
        self.grid_dir = grid_dir
        engine = create_engine(f'sqlite:///{self.db_file}')
        self.data = pd.read_sql('models', engine)

    def read_history(self, log_dir, top_dir, he4, temp_dir='.', delete_temp=True, rename=False):
        """Reads a single evolutionary model (a profile) and returns
        a MesaData object.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.
        temp_dir : str, optional
            Temporary dirctory for the required model. Default: '.'.
        delete_temp : bool, optional
            If True delete the temporary model. Default: True.
        rename : bool, optional
            If True it renames the history file to include information about
            the model contained in log_dir.

        Returns
        ----------
        MesaData
            Evolutionary model (MESA profile file) as MesaData object.
        """

        self.extract_history(log_dir, top_dir, temp_dir, rename)
        history_name = f'history{log_dir[4:]}.data' if rename else 'history.data'
        temp_file = os.path.join(temp_dir, history_name)
        data = mesa.MesaData(temp_file)
        if delete_temp:
            os.remove(temp_file)
        return data
    
    def read_evol_model(self, log_dir, top_dir, he4, temp_dir='.', delete_temp=True):
        """Reads a single evolutionary model (a profile) and returns
        a MesaData object.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.
        temp_dir : str, optional
            Temporary dirctory for the required model. Default: '.'.
        delete_temp : bool, optional
            If True delete the temporary model. Default: True.

        Returns
        ----------
        MesaData
            Evolutionary model (MESA profile file) as MesaData object.
        """

        self.extract_evol_model(log_dir, top_dir, he4, temp_dir)
        temp_file = os.path.join(temp_dir, self.evol_model_name(he4))
        data = mesa.MesaData(temp_file)
        if delete_temp:
            os.remove(temp_file)
        return data
    
    def read_puls_model(self, log_dir, top_dir, he4, temp_dir='.', delete_temp=True):
        """Reads a calculated GYRE model and returns
        a GyreData object.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.
        temp_dir : str, optional
            Temporary dirctory for the required model. Default: '.'.
        delete_temp : bool, optional
            If True delete the temporary model. Default: True.

        Returns
        ----------
        GyreData
            Pulsation model as GyreData object.
        """

        self.extract_puls_model(log_dir, top_dir, he4, temp_dir)
        temp_file = os.path.join(temp_dir, self.puls_model_name(he4))
        data = gyre_data.GyreData(temp_file)
        if delete_temp:
            os.remove(temp_file)
        return data
    
    def extract_history(self, log_dir, top_dir, dest_dir, rename=False):
        """Extracts a MESA history file.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        dest_dir : str
            Destination directory.
        rename : bool
            If True it renames the history file to include information about
            the model contained in log_dir. Default: False.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        history_name = f'history{log_dir[4:]}.data' if rename else 'history.data'
        grid_zip_path = os.path.join(top_dir, log_dir, history_name)
        dest_path = os.path.join(dest_dir, history_name)

        with ZipFile(grid_zip_file) as archive:
            with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                shutil.copyfileobj(zipped_file, dest_file)

    def extract_evol_model(self, log_dir, top_dir, he4, dest_dir):
        """Extracts a single evolutionary model (a profile).

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.
        dest_dir : str
            Destination directory.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.evol_model_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)
        dest_path = os.path.join(dest_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                    shutil.copyfileobj(zipped_file, dest_file)

    def extract_puls_model(self, log_dir, top_dir, he4, dest_dir):
        """Extracts a single calculated GYRE model.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.
        dest_dir : str
            Destination directory.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.puls_model_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)
        dest_path = os.path.join(dest_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                    shutil.copyfileobj(zipped_file, dest_file)

    def extract_gyre_input_model(self, log_dir, top_dir, he4, dest_dir):
        """Extracts a single GYRE input model.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.
        dest_dir : str
            Destination directory.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.gyre_input_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)
        dest_path = os.path.join(dest_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                    shutil.copyfileobj(zipped_file, dest_file)

    def evol_model_exists(self, log_dir, top_dir, he4):
        """Checks if a profile exists in archive.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.

        Returns
        ----------
        bool
            True if a profile exists, False otherwise.
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.evol_model_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                return True
            else:
                return False

    def puls_model_exists(self, log_dir, top_dir, he4):
        """Checks if a calculated GYRE model exists in archive.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.

        Returns
        ----------
        bool
            True if a profile exists, False otherwise.
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.puls_model_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                return True
            else:
                return False

    def gyre_input_exists(self, log_dir, top_dir, he4):
        """Checks if a GYRE input model exists in archive.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        he4 : float
            Central helium abundance of the required model.

        Returns
        ----------
        bool
            True if a profile exists, False otherwise.
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.gyre_input_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                return True
            else:
                return False

    @staticmethod
    def archive_name(top_dir):
        """Returns a name of a zip file containing a top direcotry.

        Parameters
        ----------
        top_dir : str
            Top directory.

        Returns
        ----------
        str
            Name of zipfile.
        """

        return f"grid{top_dir[4:]}.zip"

    @staticmethod
    def evol_model_name(he4):
        """Returns a name of a MESA profile for helium abundance 'he4'.

        Parameters
        ----------
        he4 : float
            Central helium abundance of the model.

        Returns
        ----------
        str
            Name of MESA profile.
        """

        return f"custom_He{round(he4, 6)}.data"

    @staticmethod
    def puls_model_name(he4):
        """Returns a name of a calculated GYRE model for helium abundance 'he4'.

        Parameters
        ----------
        he4 : float
            Central helium abundance of the model.

        Returns
        ----------
        str
            Name of calculated GYRE model.
        """

        return f"custom_He{round(he4, 6)}_summary.txt"

    @staticmethod
    def gyre_input_name(he4):
        """Returns a name of an input model for GYRE model for helium abundance 'he4'.

        Parameters
        ----------
        he4 : float
            Central helium abundance of the model.

        Returns
        ----------
        str
            Name of GYRE input model.
        """

        return f"custom_He{round(he4, 6)}.data.GYRE"


if __name__ == "__main__":
    database = '/Users/cespenar/sdb/sdb_grid_cpm.db'
    grid_dir = '/Volumes/T3_2TB/sdb/grid_sdb'
    g = SdbGridReader(database, grid_dir)

    top_dir = 'logs_mi1.0_z0.015_lvl0'
    log_dir = 'logs_mi1.0_menv0.0001_rot0.0_z0.015_y0.2715_fh0.0_fhe0.0_fsh0.0_mlt1.8_sc0.1_reimers0.0_blocker0.0_turbulence0.0_lvl0_15240'
    he4 = 0.5
    # destination = os.getcwd()
    # g.extract_evol_model(log_dir, top_dir, he4, destination)

    # data = g.read_evol_model(log_dir, top_dir, he4)
    data = g.read_puls_model(log_dir, top_dir, he4)

    # print(g.data.head())

    # df = g.data
    # plt.plot(10.0 ** df.log_Teff, df.log_g, 'k.')
    # plt.gca().invert_xaxis()
    # plt.gca().invert_yaxis()
    # plt.show()
