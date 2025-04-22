import joblib
import pandas as pd
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class EmailClassifier:
    """
    Trainer and predictor for email classification.
    """
    def __init__(self):
        self.pipeline = ImbPipeline([
            (
                'tfidf',
                TfidfVectorizer(
                    stop_words='english', max_features=10000,
                ),
            ),
            ('smote', SMOTE(random_state=42)),
            (
                'clf',
                LogisticRegression(
                    solver='saga',
                    class_weight='balanced',
                    max_iter=500,
                    n_jobs=-1,
                ),
            ),
        ])
        self.search = None

    def train(self, data_path: str) -> None:
        """
        Train the model and save the best estimator to disk.
        """
        df = pd.read_csv(data_path)
        X = df['email_translated']
        y = df['type']

        X_train, _, y_train, _ = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42,
        )

        param_grid = {'clf__C': [0.1, 1.0, 10.0]}
        self.search = GridSearchCV(
            self.pipeline, param_grid,
            cv=3, scoring='f1_macro', n_jobs=-1, verbose=1
        )
        self.search.fit(X_train, y_train)
        joblib.dump(self.search.best_estimator_, 'final_pipeline.pkl')
        logger.info("Model trained and saved as final_pipeline.pkl")

    def predict(self, text):
        model = joblib.load('final_pipeline.pkl')
        logger.info("Model loaded from final_pipeline.pkl")
        return model.predict([text])[0]
