from sklearn.decomposition import PCA


def run_pca(df):

    features = df.drop(
        columns=["lat", "lon"]
    )

    max_components = min(
        3,
        features.shape[0],
        features.shape[1]
    )

    pca = PCA(
        n_components=max_components
    )

    components = pca.fit_transform(
        features
    )

    return {
        "components": components,
        "variance": pca.explained_variance_ratio_
    }