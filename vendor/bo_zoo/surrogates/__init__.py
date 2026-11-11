from bo_zoo.surrogates.gp import GPSurrogate, ModelListGPSurrogate
from bo_zoo.surrogates.mtgp import MTGPSurrogate
from bo_zoo.surrogates.dgp import (
    DGPHiddenLayer,
    DGPLastLayer,
    MultiTaskDeepGPSurrogate,
    TrueDeepGPSurrogate,
)
from bo_zoo.surrogates.fake_model import FakeModel, ExactVariancePosterior
from bo_zoo.surrogates.tabpfn import TabPFNSurrogate
from bo_zoo.surrogates.quantile_forests import QuantileRFSurrogate, ExtraTreesQSurrogate
from bo_zoo.surrogates.gradient_boosting import GBRQuantileSurrogate, XGBQuantileSurrogate
from bo_zoo.surrogates.bayesian_ridge import BayesianRidgeSurrogate
from bo_zoo.surrogates.linear_quantile import LinearQuantileSurrogate
from bo_zoo.surrogates.model_list_quantile import ModelListQuantileSurrogate
from bo_zoo.surrogates.pbnn import PBNNSurrogate
from bo_zoo.surrogates.hybrid import HybridPosterior

__all__ = [
    "GPSurrogate",
    "ModelListGPSurrogate",
    "MTGPSurrogate",
    "DGPHiddenLayer",
    "DGPLastLayer",
    "MultiTaskDeepGPSurrogate",
    "TrueDeepGPSurrogate",
    "FakeModel",
    "ExactVariancePosterior",
    "TabPFNSurrogate",
    "QuantileRFSurrogate",
    "ExtraTreesQSurrogate",
    "GBRQuantileSurrogate",
    "XGBQuantileSurrogate",
    "BayesianRidgeSurrogate",
    "LinearQuantileSurrogate",
    "ModelListQuantileSurrogate",
    "PBNNSurrogate",
    "HybridPosterior",
]
