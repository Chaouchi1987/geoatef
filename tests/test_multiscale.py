import pandas as pd
from backend.science.multiscale import neighborhood_consensus

def test_consensus():
    df=pd.DataFrame({"lat":[35.0,35.00001,35.00002],"lon":[7.0,7.00001,7.00002],"anomaly_score":[.2,.8,.4]})
    out=neighborhood_consensus(df)
    assert "consensus_score" in out
    assert len(out)==3
