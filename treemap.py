"""
This code is mostly taken from https://plotly.com/python/treemaps/
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_hierarchical_dataframe(df, levels, value_column, color_columns=None):
    """
    Build a hierarchy of levels for Sunburst or Treemap charts.

    Levels are given starting from the bottom to the top of the hierarchy,
    ie the last level corresponds to the root.

    >>> df = pd.DataFrame([['North', 'Dallam', 'JE', 35, 23],
    ...   ['North', 'Dallam', 'ZQ', 49, 13],
    ...   ['North', 'Dallam', 'IJ', 20, 6],
    ...   ['North', 'Hartley', 'WE', 39, 37],
    ...   ['North', 'Hartley', 'PL', 42, 37]], columns = ['region', 'county', 'salesperson', 'calls', 'sales'])
    >>> build_hierarchical_dataframe(df, levels = ['salesperson', 'county', 'region'], color_columns = ['sales', 'calls'], value_column = 'calls')
            id   parent value     color
    0       IJ   Dallam    20  0.300000
    1       JE   Dallam    35  0.657143
    2       PL  Hartley    42  0.880952
    3       WE  Hartley    39  0.948718
    4       ZQ   Dallam    49  0.265306
    5   Dallam    North   104  0.403846
    6  Hartley    North    81  0.913580
    7    North    total   185  0.627027
    8    total            185  0.627027
    """
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        dfg = df.groupby(levels[i:]).sum()
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()
        if i < len(levels) - 1:
            df_tree['parent'] = dfg[levels[i+1]].copy()
        else:
            df_tree['parent'] = 'total'
        df_tree['value'] = dfg[value_column]
        df_tree['color'] = dfg[color_columns[0]] / dfg[color_columns[1]]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
    total = pd.Series(dict(id='total', parent='',
                              value=df[value_column].sum(),
                              color=df[color_columns[0]].sum() / df[color_columns[1]].sum()))
    df_all_trees = df_all_trees.append(total, ignore_index=True)
    return df_all_trees

def build_tree_map(df, average_score = 0.5, maxdepth = None, value_name = 'Label', color_name = 'Color'):
    """
    Can demonstrate a single or a number of dataframes as a hierarchical treemap and choose 
    the depth showed at any time 

    Args:
        df (dataframe or list of dataframes): mandatory columns are ['id' (label), 'parent', 'value', 'color']
        average_score (float):
        maxdepth (int): number of levels of hierarchy to show, min 2
    """
    if isinstance(df,list):
        pass
    elif isinstance(df,pd.core.frame.DataFrame):
        df=[df]
    else:
        print('df of not expected format')

    mandatory_cols = ['value', 'color', 'parent', 'id']
    for (i, df_i) in enumerate(df):
        for m in mandatory_cols:
            assert(m in df_i.columns)

    fig = make_subplots(1, len(df), specs=[[{"type": "domain"}]*len(df)],)
    
    for (i, df_all_trees) in enumerate(df):
        fig.add_trace(go.Treemap(
            ids=df_all_trees['id'],
            labels=df_all_trees['labels'],
            parents=df_all_trees['parent'],
            values=df_all_trees['value'],
            branchvalues='total',
            marker=dict(
                colors=df_all_trees['color'],
                colorscale='RdBu',
                cmid=average_score),
            hovertemplate='<b>%{label} </b> <br> '+value_name+': %{value}<br>'+color_name+': %{color:.2f}',
            name=''
            ), 1, i+1)
    if maxdepth:
        if maxdepth < 2:
            print('try maxdepth > 1')
        fig.update_traces(maxdepth=maxdepth)
    fig.update_layout(margin=dict(t = 10, b = 10, r = 10, l = 10))
    fig.show()