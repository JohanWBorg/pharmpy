import enum

import pandas as pd


class DatasetError(Exception):
    pass


class DatasetWarning(Warning):
    pass


class ColumnType(enum.Enum):
    """The type of the data in a column
    """
    UNKNOWN = enum.auto()
    ID = enum.auto()
    IDV = enum.auto()
    DV = enum.auto()
    COVARIATE = enum.auto()

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @property
    def max_one(self):
        """Can this ColumnType only be assigned to at most one column?
        """
        return self in (ColumnType.ID, ColumnType.IDV)


class PharmDataFrame(pd.DataFrame):
    """A DataFrame with additional metadata.

    Each column can have a ColumnType. The default ColumnType is UNKNOWN.

    ============  =============
    ColumnType    Description
    ============  =============
    ID            Individual identifier. Max one per DataFrame. All values have to be unique
    IDV           Independent variable. Max one per DataFrame.
    DV            Dependent variable
    COVARIATE     Covariate
    UNKOWN        Unkown type. This will be the default for columns that hasn't been assigned a type
    ============  =============

    """
    _metadata = [ '_column_types' ]

    @property
    def _constructor(self):
        return PharmDataFrame

    @property
    def _constructor_sliced(self):
        return pd.Series


class ColumnTypeIndexer:
    """Indexing a PharmDataFrame to get or set column types
       An instance of ColumnTypeIndexer can be retrieved by df.pharmpy.column_type
    """
    def __init__(self, df):
        self._obj = df

    def _set_one_column_type(self, label, tp):
        if label not in self._obj.columns:
            raise KeyError(str(label))
        try:
            self._obj._column_types[label] = tp
        except AttributeError:
            self._obj._column_types = {}
            self._obj._column_types[label] = tp

    def __setitem__(self, ind, tp):
        if isinstance(ind, str):
            self._set_one_column_type(ind, tp)
        else:
            if hasattr(tp, '__len__') and not len(tp) == 1:
                if len(ind) == len(tp):
                    for label, one_tp in zip(ind, tp):
                        self._set_one_column_type(label, one_tp)
                else:
                    raise ValueError(f'Cannot set {len(ind)} columns using {len(tp)} column types')
            else:
                # Broadcasting of tp
                for label in ind:
                    self._set_one_column_type(label, tp)

    def _get_one_column_type(self, label):
        """Get the column type of one column
        """
        if label in self._obj.columns:
            try:
                d = self._obj._column_types
            except AttributeError:
                return ColumnType.UNKNOWN
            try:
                return d[label]
            except KeyError:
                return ColumnType.UNKNOWN
        else:
            raise KeyError(str(label))

    def __getitem__(self, ind):
        if isinstance(ind, str):
            return self._get_one_column_type(ind)
        else:
            try:
                return [self._get_one_column_type(label) for label in ind]
            except TypeError:
                return self._get_one_column_type(ind)


class LabelsByTypeIndexer:
    """Indexing a PharmDataFrame to get labels from ColumnTypes
    """
    def __init__(self, acc):
        self._acc = acc

    def _get_one_label(self, tp):
        labels = self._get_many_labels(tp)
        if len(labels) == 0:
            raise KeyError(str(tp))
        elif len(labels) > 1:
            raise KeyError('Did not expect more than one ' + str(tp))
        else:
            return labels

    def _get_many_labels(self, column_type):
        """ Will raise if no columns of the type exists
            Always returns a list of labels
        """
        return [label for label in self._acc._obj.columns if self._acc.column_type[label] == column_type]

    def __getitem__(self, tp):
        try:
            if len(tp) > 1:
                labels = []
                for t in tp:
                    if t.max_one:
                        labels.extend(self._get_one_label(t))
                    else:
                        labels.extend(self._get_many_labels(t))
                return labels
            else:
                if tp[0].max_one:
                    return self._get_one_label(tp[0])
                else:
                    return self._get_many_labels(tp[0])
        except TypeError:
            if tp.max_one:
                return self._get_one_label(tp)
            else:
                return self._get_many_labels(tp)


@pd.api.extensions.register_dataframe_accessor('pharmpy')
class DataFrameAccessor:
    def __init__(self, obj):
        self._obj = obj

    @property
    def column_type(self):
        return ColumnTypeIndexer(self._obj)

    @property
    def labels_by_type(self):
        return LabelsByTypeIndexer(self)

    @property
    def id_label(self):
        """ Return the label of the id column
        """
        return self.labels_by_type[ColumnType.ID][0]

    @property
    def time_varying_covariates(self):
        """ Return a list of labels for all time varying covariates
        """
        cov_labels = self.labels_by_type[ColumnType.COVARIATE]
        if len(cov_labels) == 0:
            return []
        else:
            time_var = self._obj.groupby(by=self.id_label)[cov_labels].nunique().gt(1).any()
            return list(time_var.index[time_var])

    @property
    def covariate_baselines(self):
        """ Return a dataframe with baselines of all covariates for each id.
            Baseline is taken to be the first row even if that has a missing value.
        """
        covariates = self.labels_by_type[ColumnType.COVARIATE]
        idlab = self.id_label
        df = self._obj[covariates + [idlab]]
        return df.groupby(idlab).nth(0)
