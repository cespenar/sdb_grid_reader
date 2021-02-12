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
    """Structure containing a processed MESA grid of sdB stars.

    Reads a grid and provides methods to extract and read models.

    Parameters
    ----------
    db_file : str
        Database containing the grid of models.
    grid_dir : str
        Directory containing the zipped grid of models.

    Attributes
    ----------
    db_file : str
        Path to the input database. 
    grid_dir : str
        Path to the directory containing the zipped grid of models.
    data : DataFrame
        Pandas DataFrame containing the grid.

    Examples
    ----------
    >>> database = 'sdb_grid_cpm.db'
    >>> grid_dir = 'grid_sdb'
    >>> g = SdbGridReader(database, grid_dir)

    Here `database` is the database containing the processed grid of
    calcualted MESA sdB models and `grid_dir` is the directory containing
    the full compressed grid. The grid is then initialized.
    """

    def __init__(self, db_file, grid_dir):
        """Creates SdbGridReader object from a processed
        grid of MESA sdB models.

        Parameters
        ----------
        db_file : str
            Database containing the grid of models.
        grid_dir : str
            Directory containing the zipped grid of models.
        """
        
        self.db_file = db_file
        self.grid_dir = grid_dir
        engine = create_engine(f'sqlite:///{self.db_file}')
        self.data = pd.read_sql('models', engine)

    def read_history(self, log_dir, top_dir, he4, dest_dir='.', delete_file=True,
                     rename=False, keep_tree=False):
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
        dest_dir : str, optional
            Temporary dirctory for the required model. Default: '.'.
        delete_file : bool, optional
            If True delete the extracted model. The model is not deleted
            if 'keep_tree' is True. Default: True.
        rename : bool, optional
            If True it renames the history file to include information about
            the model contained in log_dir.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        MesaData
            Evolutionary model (MESA profile file) as MesaData object.
        """

        history_name = f'history{log_dir[4:]}.data' if rename else 'history.data'
        if keep_tree:
            file_name = os.path.join(
                dest_dir, top_dir, log_dir, self.evol_model_name(he4))
        else:
            file_name = os.path.join(dest_dir, history_name)
        if not self.model_extracted(file_name):
            self.extract_history(log_dir, top_dir, dest_dir, rename, keep_tree)
        data = mesa.MesaData(file_name)
        if delete_file and not keep_tree:
            os.remove(file_name)
        return data

    def read_evol_model(self, log_dir, top_dir, he4, dest_dir='.',
                        delete_file=True, keep_tree=False):
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
        dest_dir : str, optional
            Dirctory for the required model. Default: '.'.
        delete_file : bool, optional
            If True delete the extracted model. The model is not deleted
            if 'keep_tree' is True. Default: True.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        MesaData
            Evolutionary model (MESA profile file) as MesaData object.
        """

        if keep_tree:
            file_name = os.path.join(
                dest_dir, top_dir, log_dir, self.evol_model_name(he4))
        else:
            file_name = os.path.join(dest_dir, self.evol_model_name(he4))
        if not self.model_extracted(file_name):
            self.extract_evol_model(log_dir, top_dir, he4, dest_dir, keep_tree)
        data = mesa.MesaData(file_name)
        if delete_file and not keep_tree:
            os.remove(file_name)
        return data

    def read_puls_model(self, log_dir, top_dir, he4, dest_dir='.', delete_file=True,
                        keep_tree=False):
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
        dest_dir : str, optional
            Temporary dirctory for the required model. Default: '.'.
        delete_file : bool, optional
            If True delete the extracted model. The model is not deleted
            if 'keep_tree' is True. Default: True.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        GyreData
            Pulsation model as GyreData object.
        """

        if keep_tree:
            file_name = os.path.join(
                dest_dir, top_dir, log_dir, self.puls_model_name(he4))
        else:
            file_name = os.path.join(dest_dir, self.puls_model_name(he4))
        if not self.model_extracted(file_name):
            self.extract_puls_model(log_dir, top_dir, he4, dest_dir, keep_tree)
        data = gyre_data.GyreData(file_name)
        if delete_file and not keep_tree:
            os.remove(file_name)
        return data

    def extract_history(self, log_dir, top_dir, dest_dir, rename=False, keep_tree=False):
        """Extracts a MESA history file.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        dest_dir : str
            Destination directory for the extracted model if 'keep_tree' is False,
            or the root direcotry if 'keep_tree' is True.
        rename : bool
            If True it renames the history file to include information about
            the model contained in log_dir. Default: False.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        history_name = f'history{log_dir[4:]}.data' if rename else 'history.data'
        grid_zip_path = os.path.join(top_dir, log_dir, history_name)
        dest_path = os.path.join(dest_dir, history_name)

        with ZipFile(grid_zip_file) as archive:
            if keep_tree:
                archive.extract(grid_zip_path, dest_dir)
            else:
                with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                    shutil.copyfileobj(zipped_file, dest_file)

    def extract_evol_model(self, log_dir, top_dir, he4, dest_dir, keep_tree=False):
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
            Destination directory for the extracted model if 'keep_tree' is False,
            or the root direcotry if 'keep_tree' is True.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.evol_model_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)
        dest_path = os.path.join(dest_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                if keep_tree:
                    archive.extract(grid_zip_path, dest_dir)
                else:
                    with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                        shutil.copyfileobj(zipped_file, dest_file)

    def extract_puls_model(self, log_dir, top_dir, he4, dest_dir, keep_tree=False):
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
            Destination directory for the extracted model if 'keep_tree' is False,
            or the root direcotry if 'keep_tree' is True.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.puls_model_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)
        dest_path = os.path.join(dest_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                if keep_tree:
                    archive.extract(grid_zip_path, dest_dir)
                else:
                    with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                        shutil.copyfileobj(zipped_file, dest_file)

    def extract_gyre_input_model(self, log_dir, top_dir, he4, dest_dir, keep_tree=False):
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
            Destination directory for the extracted file if 'keep_tree' is False,
            or the root direcotry if 'keep_tree' is True.
        keep_tree : bool, optional
            If True extract file with its directory structure (default
            ZipFile.extract behaviour), otherwise extract file directly to
            'dest_dir'. Default: False.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        model_name = self.gyre_input_name(he4)
        grid_zip_path = os.path.join(top_dir, log_dir, model_name)
        dest_path = os.path.join(dest_dir, model_name)

        with ZipFile(grid_zip_file) as archive:
            if grid_zip_path in archive.namelist():
                if keep_tree:
                    archive.extract(grid_zip_path, dest_dir)
                else:
                    with archive.open(grid_zip_path) as zipped_file, open(dest_path, 'wb') as dest_file:
                        shutil.copyfileobj(zipped_file, dest_file)

    def extract_log_dir(self, log_dir, top_dir, dest_dir):
        """Extracts a MESA log directory.

        Parameters
        ----------
        log_dir : str
            Log directory.
        top_dir : str
            Top directory.
        dest_dir : str
            Destination directory for the extracted directory tree.

        Returns
        ----------
        """

        grid_zip_file = os.path.join(self.grid_dir, self.archive_name(top_dir))
        grid_zip_path = os.path.join(top_dir, log_dir)

        with ZipFile(grid_zip_file) as archive:
            for f_name in archive.namelist():
                if f_name.startswith(grid_zip_path):
                    archive.extract(f_name, dest_dir)

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
    def model_extracted(path):
        """Checks if model is already exracted.

        Parameters
        ----------
        path : str
            Path to the model.

        Returns
        ----------
        bool
            True if model exists, False otherwise.
        """

        if os.path.isfile(path):
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
    destination = os.getcwd()
    # g.extract_evol_model(log_dir, top_dir, he4, destination, keep_tree=True)
    # g.extract_log_dir(log_dir, top_dir, destination)

    # data = g.read_evol_model(log_dir, top_dir, he4, keep_tree=True)
    # data = g.read_puls_model(log_dir, top_dir, he4)

    # print(g.data.head())

    # df = g.data
    # plt.plot(10.0 ** df.log_Teff, df.log_g, 'k.')
    # plt.gca().invert_xaxis()
    # plt.gca().invert_yaxis()
    # plt.show()
