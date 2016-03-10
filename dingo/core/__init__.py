from dingo.core.network import stations
from dingo.tools import config as cfg_dingo
from oemof import db

import networkx as nx
import pandas as pd
import geopandas as gpd
from geopy.distance import vincenty

class NetworkDingo():
    """ DINGO Network, contains the NetworkX graph and associated attributes.
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.mv_region = kwargs.get('mv_region', None)

        self.graph = nx.Graph()

    def convert_to_networkx(self):
        #entities = self.entities
        #buses = [e for e in entities if isinstance(e, BusPypo)]
        #generators = [e for e in entities if isinstance(e, GenPypo)]
        #branches = [e for e in entities if isinstance(e, BranchPypo)]
        self.graph.add_nodes_from(self.transformers)
        #graph.add_nodes_from(self.transformers + self.buses)
        #positions = nx.spectral_layout(graph)
        return graph

    def draw_networkx(self, graph):
        positions = {}
        #positions_b = {}
        for t in self.transformers:
            positions[t] = [t.geo_data.x, t.geo_data.y]
        #for b in self.buses:
        #    positions_b[b] = [b.geo_data.x, b.geo_data.y]
        #positions[] = [[t.geo_data.x, t.geo_data.y] for t in self.transformers]
        nx.draw_networkx_nodes(graph, positions, self.transformers, node_shape="o", node_color="r",
                               node_size = 5)
        #nx.draw_networkx_nodes(graph, positions_b, self.buses, node_shape="o", node_color="b",
        #                       node_size = 2
        plt.show()

#        for e in entities:
#            for e_in in e.inputs:
#                g.add_edge(e_in, e)
#        if positions is None:
#            positions = nx.spectral_layout(g)
#        nx.draw_networkx_nodes(g, positions, buses, node_shape="o", node_color="r",
#                               node_size = 600)
#        nx.draw_networkx_nodes(g, positions, branches, node_shape="s",
#                               node_color="b", node_size=200)
#        nx.draw_networkx_nodes(g, positions, generators, node_shape="s",
#                               node_color="g", node_size=200)
#        nx.draw_networkx_edges(g, positions)
#        if labels:
#            nx.draw_networkx_labels(g, positions)
#        plt.show()
#        if not nx.is_connected(g):
#            raise ValueError("Graph is not connected")

    def import_mv_stations(self, conn, id=None):
        """imports MV-stations from database"""

        schema_table = cfg_dingo.get('stations', 'mv_stations')
        #schema, table = cfg_dingo.get('stations', 'mv_stations').split('.')
        index_col = 'subst_id'
        #columns = ['subst_id', 'geom']
        srid = '4326'

        #mv_stations = pd.read_sql_table(table, conn, schema=schema,
        #                                index_col=index_col, columns=columns)

        # build SQL query
        where_clause = ''
        if id:
            where_clause =  'WHERE subst_id=' + str(id)
        sql = """SELECT subst_id,
                        ST_AsText(ST_TRANSFORM(geom, {})) as geom
                        FROM {} {};""".format(srid, schema_table, where_clause)

        # read data from db
        mv_stations = pd.read_sql_query(sql, conn, index_col)

        #sql2 = 'SELECT ' + ', '.join(columns) + ' FROM ' + schema + '.' + table + ';'
        #sql = '''SELECT subst_id,
        #         geom
        #         FROM voronoi.substations_excldbahn;'''
        #mv_stations2 = gpd.read_postgis(sql2,conn)
        #y = gpd.GeoDataFrame.from_postgis(sql,conn)

        # create objects from rows and add them to graph
        for idx, row in mv_stations.iterrows():
            station_obj = stations.MVStationDingo(name='USW_'+str(idx), geo_data=row['geom'])
            self.graph.add_node(station_obj)

    def import_lv_regions(self, conn):
        schema_table = cfg_dingo.get('regions', 'lv_regions')
        index_col = 'subst_id'
        srid = '4326'

        # build SQL query
        where_clause = ''
        if id:
            where_clause =  'WHERE subst_id=' + str(id)
        sql = """SELECT subst_id,
                        ST_AsText(ST_TRANSFORM(geom, {})) as geom
                        FROM {} {};""".format(srid, schema_table, where_clause)

        # read data from db
        mv_stations = pd.read_sql_query(sql, conn, index_col)