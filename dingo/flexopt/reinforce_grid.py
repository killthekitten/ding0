"""This file is part of DINGO, the DIstribution Network GeneratOr.
DINGO is a tool to generate synthetic medium and low voltage power
distribution grids based on open data.

It is developed in the project open_eGo: https://openegoproject.wordpress.com

DINGO lives at github: https://github.com/openego/dingo/
The documentation is available on RTD: http://dingo.readthedocs.io"""

__copyright__  = "Reiner Lemoine Institut gGmbH"
__license__    = "GNU Affero General Public License Version 3 (AGPL-3.0)"
__url__        = "https://github.com/openego/dingo/blob/master/LICENSE"
__author__     = "nesnoj, gplssm"


from .check_tech_constraints import check_load, check_voltage, \
    assign_line_loading
from .reinforce_measures import reinforce_branches_current, \
    reinforce_branches_voltage
import logging


logger = logging.getLogger('dingo')


def reinforce_grid(grid, mode):
    """ Evaluates grid reinforcement needs and performs measures. This function
        is the parent function for all grid reinforcements.

    Parameters
    ----------
    grid: GridDingo object
    mode: String
        kind of grid ('MV' or 'LV')

    Notes
    -----
    Currently only MV branch reinforcement is implemented. HV-MV stations are not
    reinforced since not required for status-quo scenario.

    References
    ----------
    .. [1] dena VNS
    .. [2] Ackermann et al. (RP VNS)

    """

    # kind of grid to be evaluated (MV or LV)
    if mode == 'MV':
        crit_branches, crit_stations = check_load(grid, mode)

        # STEP 1: reinforce branches

        # do reinforcement
        reinforce_branches_current(grid, crit_branches)

        # if branches or stations have been reinforced: run PF again to check for voltage issues
        if crit_branches or crit_stations:
            grid.network.run_powerflow(conn=None, method='onthefly')

        crit_nodes = check_voltage(grid, mode)
        crit_nodes_count_prev_step = len(crit_nodes)

        # as long as there are voltage issues, do reinforcement
        while crit_nodes:
            # determine all branches on the way from HV-MV substation to crit. nodes
            crit_branches_v = grid.find_and_union_paths(grid.station(), crit_nodes)

            # do reinforcement
            reinforce_branches_voltage(grid, crit_branches_v)

            # run PF
            grid.network.run_powerflow(conn=None, method='onthefly')

            crit_nodes = check_voltage(grid, mode)

            # if there are critical nodes left but no larger cable available, stop reinforcement
            if len(crit_nodes) == crit_nodes_count_prev_step:
                logger.warning('==> There are {0} branches that cannot be '
                               'reinforced (no appropriate cable '
                               'available).'.format(
                    len(grid.find_and_union_paths(grid.station(),
                                                        crit_nodes))))
                break

            crit_nodes_count_prev_step = len(crit_nodes)

        if not crit_nodes:
            logger.info('==> All voltage issues could be solved using '
                        'reinforcement.')

        # STEP 2: reinforce HV-MV station
        # NOTE: HV-MV station reinforcement is not required for status-quo
        # scenario since HV-MV trafos already sufficient for load+generation
        # case as done in MVStationDingo.choose_transformers()

    elif mode == 'LV':
        assign_line_loading(grid)
        # raise NotImplementedError
